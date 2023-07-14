#!/usr/bin/perl
####################################################################################
#Author: Yuanhao Cheng, Wei Ding
#Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
#Created time: 2022/06/16
#Last Edit: 2023/06/16
#Group: SM6, The Institute of Physics, Chinese Academy of Sciences
####################################################################################
use strict;
use warnings;
use Getopt::Long;

my $mode; my $EM_dir; my $USB_dir; my $INFO_dir; my $job_name; my $raw_n;
my $rmi; my $rename_file; my $diskspace; my $psize; my $total_dose; my $acv; my $file_postfix;

GetOptions(
	'mode=i' 		=>\$mode,
	'EM_dir=s' 		=>\$EM_dir, #电镜文件夹
	'USB_dir=s'		=>\$USB_dir, #目标文件夹
	'INFO_dir=s'	=>\$INFO_dir,
	'job=s'			=>\$job_name,
	'raw_num=i'		=>\$raw_n,
	'rmi=i'			=>\$rmi,
	'rename_file=s'  =>\$rename_file,
	'disk_space=i'	=>\$diskspace, 
	'psize=f' 		=>\$psize,
    'total_dose=f' 	=>\$total_dose,
    'acv=i' 		=>\$acv, #加速电压
    'file_postfix=s' =>\$file_postfix); #文件名后缀

unless($mode && $EM_dir && $USB_dir && $job_name && $raw_n && $rename_file && $diskspace && $psize && $total_dose) 
{
	print "$0 使用方法：\n*必要参数*\t解释\n"; 
	print "\t-mode \t1: 计数; 2: 超高分辨\n";
	print "\t-INFO_dir \t记录文件夹\n";
	print "\t-USB_dir \t目标文件夹\n\t-EM_dir \t电镜文件夹\n";
	print "\t-job \t任务名称\n";
	print "\t-psize \t像素尺寸\n";
	print "\t-total_dose \t总剂量 (e/A2)\n";
	print "\t-rmi \t1: 转移文件至硬盘; 2: 不转移\n";
	print "\t-raw_n \t初始编号\n";
	print "\t-rename_file \t需要转移的文件名\n";
	print "\t-disk_space\t90%\t硬盘已用比例\n";
	exit;
}
my $rename_profix_num = sprintf "%04d", $raw_n; #输出有格式的字符串
my $rename_remain_num = 0;
my $INFO_record = "${INFO_dir}${job_name}_file_record";
my $motioncorr_dir = "${USB_dir}MotionCorr/"; #motioncorr文件夹

#记录一下当前时间
my ($sec,$min,$hour,$day,$mon,$year,$wday,$yday,$isdst) = localtime();
my $datestring = localtime();
$year = 1900+$year;
$mon = $mon+1;
print "$year-$mon-$day $hour:$min:$sec\n";

#移动照片文件并将所耗时间写在一个新的文件里
`ls|time -o "${INFO_dir}${job_name}_${rename_profix_num}_mv_time" -p cp $rename_file ${USB_dir}${job_name}_${rename_profix_num}$file_postfix`;
#提取刚刚写的所耗时间
my $real_mv_time = `awk '/real/' "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`; 
`rm -rf "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`; 
chomp($real_mv_time);
my @mv_time = split (/\s+/, $real_mv_time);
my $total_time = $mv_time[1];

#for (my $i=1; $i <= 10; $i++) {
#	if (-e $rename_file) {
#		sleep(5);
#		print "$rename_file requires additional $i moves\n";
#		`ls|time -o "${INFO_dir}${job_name}_${rename_profix_num}_mv_time" -p cp $rename_file "${cal_dir}${job_name}_${rename_profix_num}$file_postfix"`;
#		$real_mv_time = `awk '/real/' "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
#		`rm -rf "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
#		chomp($real_mv_time);
#		@mv_time = split (/\s+/, $real_mv_time);
#		$total_time = $total_time + $mv_time[1] + 5;}
#	else	{last;}}

#检查照片张数
my $frame_num = `frames_counter.py ${USB_dir}${job_name}_${rename_profix_num}$file_postfix | grep total`;
$frame_num =~ s/\ frames\ total$//;
print "$rename_file 照片帧数：$frame_num";
chomp($frame_num);
my $dose_per_frame = $total_dose / $frame_num;

my $gpu_num = 0; my $log_line; my @element_log_line;
if ($mode == 2) 
{
	if ($raw_n > 8999) 
	{
		#system "mv ${cal_dir}${job_name}_${rename_profix_num}.tif ${cal_dir}${job_name}_${rename_profix_num}_imod.tif";
		system "ls|time -o ${INFO_dir}${job_name}_${rename_profix_num}_mv_time -p MotionCor2_1.6.4_Cuda121_Mar312023 -InTiff ${USB_dir}${job_name}_${rename_profix_num}$file_postfix -OutMrc ${motioncorr_dir}${job_name}_${rename_profix_num}_SumCorr.mrc -Gain ${USB_dir}gain_8bit.mrc -LogDir ${motioncorr_dir} -Patch 7 5 20 -Bft 500 -FtBin 2 -Iter 20 -Tol 0.5 -Throw 3 -FmDose $dose_per_frame -PixSize $psize -kV $acv -SumRange 0 0 -Gpu $gpu_num >> ${INFO_dir}${job_name}_motioncorr.log";
		$real_mv_time = `awk '/real/' "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		`rm -rf "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		chomp($real_mv_time);                
		@mv_time = split (/\s+/, $real_mv_time);
		$total_time = $total_time + $mv_time[1];
		print "$diskspace% disk space used... Moving $rename_file to ${USB_dir}${job_name}_${rename_profix_num}$file_postfix takes time $total_time sec\n";
	}
	else	
	{
		# MotionCor2进行漂移修正并且把照片叠加 Using MotionCor2 to do motion correction
		print "MotionCor2_1.6.4_Cuda121_Mar312023 -InTiff ${USB_dir}${job_name}_${rename_profix_num}$file_postfix -OutMrc ${motioncorr_dir}${job_name}_${rename_profix_num}_SumCorr.mrc -Gain ${USB_dir}gain_8bit.mrc -LogDir ${motioncorr_dir} -Patch 7 5 20 -Bft 500 -FtBin 2 -Iter 20 -Tol 0.5 -Throw 3 -FmDose $dose_per_frame -PixSize $psize -kV $acv -SumRange 0 0 -Gpu $gpu_num\n";
		system "ls|time -o ${INFO_dir}${job_name}_${rename_profix_num}_mv_time -p MotionCor2_1.6.4_Cuda121_Mar312023 -InTiff ${USB_dir}${job_name}_${rename_profix_num}$file_postfix -OutMrc ${motioncorr_dir}${job_name}_${rename_profix_num}_SumCorr.mrc -Gain ${USB_dir}gain_8bit.mrc -LogDir ${motioncorr_dir} -Patch 7 5 20 -Bft 500 -FtBin 2 -Iter 20 -Tol 0.5 -Throw 3 -FmDose $dose_per_frame -PixSize $psize -kV $acv -SumRange 0 0 -Gpu $gpu_num >> ${INFO_dir}${job_name}_motioncorr.log";
		$real_mv_time = `awk '/real/' "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		`rm -rf "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		chomp($real_mv_time);
		@mv_time = split (/\s+/, $real_mv_time);
		$total_time = $total_time + $mv_time[1];
		print "$diskspace% disk space used... Moving $rename_file to ${USB_dir}${job_name}_${rename_profix_num}$file_postfix takes time $total_time sec\n";

		$log_line = "1 2 3 4 no info";
		@element_log_line = split(/\ +/,$log_line);
		open (TMPfile1,">>$INFO_record");
		print TMPfile1 ("$rename_file ${USB_dir}${job_name}_${rename_profix_num}$file_postfix $element_log_line[4] $element_log_line[5]\n");
		close (TMPfile1);
	}
}	
elsif ($mode == 1) 
{
	if ($raw_n < 8999) 
	{
		#system "mv ${cal_dir}${job_name}_${rename_profix_num}.tif ${cal_dir}${job_name}_${rename_profix_num}_imod.tif";
		#print "mv ${cal_dir}${job_name}_${rename_profix_num}.tif ${cal_dir}${job_name}_${rename_profix_num}_imod.tif\n";
		print "ls|time -o ${INFO_dir}${job_name}_${rename_profix_num}_mv_time -p MotionCor2_1.6.4_Cuda121_Mar312023 -InTiff ${USB_dir}${job_name}_${rename_profix_num}$file_postfix -OutMrc ${motioncorr_dir}${job_name}_${rename_profix_num}_SumCorr.mrc -Gain ${USB_dir}gain_8bit.mrc -LogDir ${motioncorr_dir} -Patch 7 5 20 -Bft 500 -FtBin 2 -Iter 20 -Tol 0.5 -Throw 3 -FmDose $dose_per_frame -PixSize $psize -kV $acv -SumRange 0 0 >> ${INFO_dir}${job_name}_motioncorr.log\n";
		system "ls|time -o ${INFO_dir}${job_name}_${rename_profix_num}_mv_time -p MotionCor2_1.6.4_Cuda121_Mar312023 -InTiff ${USB_dir}${job_name}_${rename_profix_num}$file_postfix -OutMrc ${motioncorr_dir}${job_name}_${rename_profix_num}_SumCorr.mrc -Gain ${USB_dir}gain_8bit.mrc -LogDir ${motioncorr_dir} -Patch 7 5 20 -Bft 500 -FtBin 2 -Iter 20 -Tol 0.5 -Throw 3 -FmDose $dose_per_frame -PixSize $psize -kV $acv -SumRange 0 0 -Gpu $gpu_num >> ${INFO_dir}${job_name}_motioncorr.log";
		$real_mv_time=`awk '/real/' "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		`rm -rf "${INFO_dir}${job_name}_${rename_profix_num}_mv_time"`;
		chomp($real_mv_time);
		@mv_time = split (/ +/, $real_mv_time);
		$total_time = $total_time + $mv_time[1];
	    print "$diskspace% disk space used... Moving $rename_file to ${USB_dir}${job_name}_${rename_profix_num}$file_postfix takes time $total_time sec\n";

		$log_line="1 2 3 4 no info";
		@element_log_line = split(/\s+/,$log_line);
		open (TMPfile1,">>$INFO_record");
		print TMPfile1 ("$rename_file ${USB_dir}${job_name}_${rename_profix_num}$file_postfix $element_log_line[4] $element_log_line[5]\n");
		close (TMPfile1);
	}
	else   
	{
	    my $file_9000 = 0;
        if (-e "${USB_dir}${job_name}_${rename_profix_num}$file_postfix") {
			$file_9000 = `ls ${USB_dir}${job_name}_${rename_profix_num}$file_postfix | wc -l`;
			chomp($file_9000);}
        my $a = 1;
	}
}
print "Auto_mv_corr finished ${job_name}_${rename_profix_num}!\n"; 
exit;
