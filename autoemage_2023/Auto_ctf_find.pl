#!/usr/bin/perl
############################################################################################################
#Author: Yuanhao Cheng, Wei Ding
#Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
#Created time: 2022/06/16
#Last Edit: 2023/06/16
#Group: SM6, The Institute of Physics, Chinese Academy of Sciences
############################################################################################################
use strict;
use warnings;
use Getopt::Long;
use Benchmark;

my $mode; my $INFO_dir; my $USB_dir; my $job_name; my $rmi; 
my $psize; my $total_dose; my $bin; my $acv; my $SpA; my $ac; my $sps; 
my $min_r; my $max_r; my $min_d; my $max_d; my $dss; my $exa; my $phase;
my $min_Pshift; my $max_Pshift; my $PS_step; my $thr; my $ctf_a_name;
my $space_limit; my $stack_size; my $obj_stigma_x; my $obj_stigma_y;
my $year; my $mon; my $day; my $hour; my $minute; my $dmin; my $dmax;
GetOptions(
	'mode=i' 		=>\$mode,
	'INFO_dir=s'	=>\$INFO_dir,
	'USB_dir=s'		=>\$USB_dir,
	'job=s'			=>\$job_name,
	'rmi=i'			=>\$rmi,
	'psize=f' 		=>\$psize,
	'total_dose=f' 	=>\$total_dose,
	'bin=i'			=>\$bin,
	'acv=i' 		=>\$acv,
	'SpA=f' 		=>\$SpA,
	'ac=f' 			=>\$ac,
	'sps=f' 		=>\$sps,
	'min_r=f' 		=>\$min_r,
	'max_r=f' 		=>\$max_r,
	'min_d=f' 		=>\$min_d,
	'max_d=f' 		=>\$max_d,
	'dss=f' 		=>\$dss,
	'exa=f' 		=>\$exa,
	'phase=i' 		=>\$phase,
	'min_Pshift=f' 	=>\$min_Pshift,
	'max_Pshift=f' 	=>\$max_Pshift,
	'PS_step=f' 		=>\$PS_step,
	'thr=i' 		=>\$thr,
	'ctf_a_name=s'		=>\$ctf_a_name,
	'drive_space=i' 	=>\$space_limit,
	'stack_size=f'		=>\$stack_size,
	'obj_stigma_x=f'	=>\$obj_stigma_x,
	'obj_stigma_y=f'	=>\$obj_stigma_y,
	'y=i'			=>\$year,
	'mon=i'		=>\$mon,
	'day=i'		=>\$day,
	'h=i' 			=>\$hour,
	'm=i' 			=>\$minute,
	'dmin=i' 		=>\$dmin,
	'dmax=i' 		=>\$dmax);
        
unless($mode && $job_name && $INFO_dir && $USB_dir && $psize && $space_limit && $total_dose) {
	print "$0 使用方法：\n*必要参数*\t解释\n"; 
	print "\t-mode \t1: 计数; 2: 超高分辨\n";
	print "\t-INFO_dir \t记录文件夹\n";
	print "\t-USB_dir \t目标文件夹\n";
	print "\t-job \t任务名称\n";
	print "\t-psize\t像素尺寸\n";
	print "\t-drive_space\t最大存储容量\n";
	print "[可选参数]\t默认值\t解释\n";
	print "\t-acv\t300.0\t加速电压\n";
	print "\t-SpA\t1.4\t球面像差\n";
	print "\t-ac\t0.1\t振幅对比度\n";
	print "\t-sps\t512\t计算功率谱所用正方形大小\n";
	print "\t-min_r\t30.0\t最小分辨率\n";
	print "\t-max_r\t5.0\t最大分辨率\n";
	print "\t-min_d\t5000.0\t最小像散\n";
	print "\t-max_d\t50000.0\t最大像散\n";
	print "\t-dss\t500\t像散搜索步长\n";
	print "\t-exa\t100\t预期像散\n";
	print "\t-phase\t1\t是否计算额外相位移动？ 1 是; 2 否\n";
	print "\t-min_Pshift\t0.0\t最小相位移动 (radian)\n";
	print "\t-max_Pshift\t3.15\t最大相位移动 (radian)\n";
	print "\t-PS_step\t0.5\t相位移动搜索步长\n";
	print "\t-thr_p\t1\tctffind 线程数\n";
	print "\t-stack_size\tmrcs stack 文件大小 (例如：2080375808)\n";
	print "\t-obj_stigma_x\t0\tthe current objective stigma x value\n";
	print "\t-obj_stigma_y\t0\tthe current objective stigma y value\n";
	exit;}
	
unless ($acv) {$acv=300.0}		
unless ($SpA) {$SpA=1.4}		
unless ($ac) {$ac=0.1}		
unless ($sps) {$sps=512}		
unless ($min_r) {$min_r=30.0}		
unless ($max_r) {$max_r=5.0}		
unless ($min_d) {$min_d=5000.0}		
unless ($max_d) {$max_d=50000.0}		
unless ($dss) {$dss=500.0}		
unless ($exa) {$exa=100.0}		
unless ($phase) {$phase=2}
unless ($min_Pshift) {$min_Pshift=0.0}
unless ($max_Pshift) {$max_Pshift=3.15}
unless ($PS_step) {$PS_step=0.5}
unless ($thr) {$thr=1}
unless ($stack_size) {$stack_size=2080375808}
unless ($obj_stigma_x) {$obj_stigma_x=0}
unless ($obj_stigma_y) {$obj_stigma_y=0}
unless ($bin) {$bin=1}

my $t0; my $t1; my $t2;
$t0 = Benchmark->new;

my $ctf_postfix = "_ctf.mrc";
my $SumCorr_postfix = "_SumCorr_DW.mrc";
my $file_postfix = ".tiff";
#my $ctffind4_postfix = "_SumCorr_ctffind4.log";
my $SumCorr_mrc = "${ctf_a_name}$SumCorr_postfix"; #ctf 输入文件名 (无路径)
my $ctf_output_file = "${ctf_a_name}$ctf_postfix"; #ctf 输出文件名 (无路径)
my $ctf_dir = "${USB_dir}CtfFind/"; #ctf文件夹
my $motioncorr_dir = "${USB_dir}MotionCorr/"; #motioncorr文件夹
#my $ctf_values = "${ctf_dir}$job_name";

chdir $ctf_dir;
#-------ctf estimation----------	
if ($mode == 2) {$psize = 2 * $psize} #超分辨率模式
#生成ctffind输入文件
open (CTFfile,">${ctf_a_name}.SumCorr.ctf.para");
if ($phase == 1) {
	$max_r = $psize * 2.1;
	$min_d = 2000;
	$max_d = 20000;
	print CTFfile ("$SumCorr_mrc\n$ctf_output_file\n$psize\n$acv\n$SpA\n$ac\n$sps\n$min_r\n$max_r\n$min_d\n$max_d\n$dss\nno\nno\nyes\n$exa\nyes\n$min_Pshift\n$max_Pshift\n$PS_step\nno\n");
       	}
else  	{
	print CTFfile ("$SumCorr_mrc\n$ctf_output_file\n$psize\n$acv\n$SpA\n$ac\n$sps\n$min_r\n$max_r\n$min_d\n$max_d\n$dss\nno\nno\nyes\n$exa\nno\nno\n");
	print "${motioncorr_dir}$SumCorr_mrc\n$ctf_output_file\n$psize\n$acv\n$SpA\n$ac\n$sps\n$min_r\n$max_r\n$min_d\n$max_d\n$dss\nno\nno\nyes\n$exa\nno\nno\n";
	}
close (CTFfile);

system  "cat ${ctf_a_name}.SumCorr.ctf.para | ctffind >> ${INFO_dir}${job_name}_ctf.log"; #ctf计算
print "cat ${ctf_a_name}.SumCorr.ctf.para | ctffind >> ${INFO_dir}${job_name}_ctf.log\n";

my $ctftxt_file = "${ctf_a_name}_ctf.txt"; my $t = 0;
my @element; my $line; my $stigma;
while ($t < 1) 
{
	if (-e "${ctftxt_file}") {
		$line = `awk '/1.000000/' $ctftxt_file`;
		$ctftxt_file =~ s/.{8}$//; #去掉末尾长度为8的字母/数字
		@element = split / +/, $line;
		$stigma = $element[2] - $element[1]; 
		$stigma = sprintf ("%.2f",$stigma);
		$stigma =~ s/^[-]{1}//; #去掉开头的-
		$element[4] = $element[4] / 3.14; 
		$element[4] = sprintf("%.2f",$element[4]);
		$t++}
	else {sleep(10);}
}
if ($element[4] > 0.7) 
{
	if ($phase == 1) 
	{
		open (CTFfile,">${ctf_a_name}.SumCorr.ctf.para");
        	$max_r = $psize * 2.1; $min_d = 2000; $max_d = 20000;
	        print CTFfile ("$SumCorr_mrc\n$ctf_output_file\n$psize\n$acv\n$SpA\n$ac\n$sps\n$min_r\n$max_r\n$min_d\n$max_d\n$dss\nno\nyes\nyes\n$exa\nyes\n$min_Pshift\n$max_Pshift\n$PS_step\nno\n");
		close (CTFfile);
		system  "cat ${ctf_a_name}.SumCorr.ctf.para | ctffind >> ${INFO_dir}${job_name}_ctf.log";
		print "cat ${ctf_a_name}.SumCorr.ctf.para | ctffind >> ${INFO_dir}${job_name}_ctf.log\n";
		$ctftxt_file = "${ctf_a_name}_ctf.txt";
		$line = `awk '/1.000000/' $ctftxt_file`;
		$ctftxt_file =~ s/.{8}$//;
		@element = split (/ +/, $line);
		$stigma = $element[2] - $element[1];
		$stigma = sprintf ("%.6f",$stigma);
		$stigma =~ s/^[-]{1}//; #CtfAstigmatism
		$element[4] = $element[4] / 3.14;
		$element[4] = sprintf("%.2f",$element[4]);
	}
}
my $defocus = $element[1]/10000; #以 Angstrom 为单位
$defocus = sprintf("%.2f", $defocus);	
$element[1] = sprintf("%.6f",$element[1]); #defocusU
$element[2] = sprintf("%.6f",$element[2]); #defocusV
$element[3] = sprintf("%.6f",$element[3]); #azimuth of astigmatism
$element[5] = sprintf("%.6f",$element[5]); #cross correlation
$element[6] = sprintf("%.6f",$element[6]); #CtfMaxResolution

#用contrast_mean检查照片的平均对比度
#my $contrast_mean_result = `contrast_mean $SumCorr_mrc | grep Contrast_Mean`;
#print "contrast_mean $SumCorr_mrc | grep Contrast_Mean\n";
#print "${contrast_mean_result}\n";
#my @contrast_mean = split(/ +/,$contrast_mean_result);
#chomp($contrast_mean[5]);
#$contrast_mean[0] = $contrast_mean[5];

my $frame_num = `frames_counter.py ${USB_dir}${ctf_a_name}$file_postfix | grep total`;
$frame_num =~ s/\ frames\ total$//;
print "${USB_dir}${ctf_a_name}$file_postfix";
chomp($frame_num);

#my $mean_value;
#if ($mode == 1) 
#{
#	$mean_value = 0.05 * $contrast_mean[0] * ( 1 / $psize ) * ( 1 / $psize );
#}
#else    
#{
#	$mean_value = 5.1 * $contrast_mean[0] * ( 1 / $psize ) * ( 1 / $psize );
#}
			
my $stack = "${USB_dir}${ctf_a_name}$file_postfix";
unless (-e "${USB_dir}${ctf_a_name}$file_postfix") 
{
	$stack = "${USB_dir}${ctf_a_name}$file_postfix";
}
	
#提取 tiff 文件大小
my $tif_size = `du -b $stack`;
$tif_size =~ s/\s+$stack//;
chomp($tif_size);

#if ($phase == 1) {$mean_value = 1.088 * $mean_value;}

my $image_num = $ctf_a_name;
$image_num =~ s/^${job_name}_//;
#if ($image_num > 8999) {$mean_value = 20.111;}

#计算冰厚
#$mean_value = sprintf "%.3f", $mean_value;
#my $thickness = 368 * log ($total_dose / $mean_value);
#$thickness = sprintf("%.1f",$thickness);

#my $collection_time1 = `date -r "$stack" "+%s"`; #以秒为单位记录流逝时间
#my $collection_time2 = `date -r "$stack" "+%F\ %R"`; #显示文件创建时间，格式为2022-04-07 20:53
#chomp($collection_time1);
#chomp($collection_time2);

#my $storage_time_s; my @name_s; my $storage_time;
#$storage_time_s = `awk '/takes time/' ${INFO_dir}${job_name}_auto_mv_corr.log | grep $ctf_a_name | tail -1`;
#@name_s = split /\ /, $storage_time_s;
#$storage_time = $name_s[-2]; #提取转移文件所耗时间
#open (TMPfile,">>$ctf_values");
#print TMPfile ("$mean_value\t$tif_size\t$collection_time1\t$ctftxt_file\t$element[1]\t$element[2]\t$stigma\t$element[3]\t$element[5]\t$element[6]\t$storage_time\t$collection_time2\t$element[4]\t$frame_num\t$thickness\n");
#close (TMPfile);
	
#my $magnification;
#$magnification = 5 * 10000 / $psize;
#$magnification = sprintf("%.1f", $magnification);
#open (TMPfile,">${ctf_a_name}$ctffind4_postfix");
#print TMPfile ("\n CS[mm], HT[kV], AmpCnst, XMAG, DStep[um]\n  2.7    $acv     0.07	   $magnification   5.000\n");
#print TMPfile ("\n   $element[1]    $element[2]    $element[3]    $element[5]  Final Values\n\n");
#print TMPfile ("Estimated defocus values        : $element[1] , $element[2] Angstroms\n");
#print TMPfile ("Estimated azimuth of astigmatism: $element[3] degrees\n");
#print TMPfile ("Additional phase shift          : $element[4] pi\n");
#print TMPfile ("Score                           : $element[5]\n");
#print TMPfile ("Thon rings with good fit up to  : $element[6]\n");
#close (TMPfile);

#my $num_start = $file_num - 9;
my @ctf_name_array = split /_/, $ctf_a_name;
my $num_name = $ctf_name_array[1];
open (Starfile, ">>micrograph_${num_name}_ctf.star");
print Starfile ("CtfFind/${ctf_a_name}_SumCorr_DW.mrc            1 CtfFind/${ctf_a_name}_ctf.mrc $element[1] $element[2]   $stigma    $element[3]     $element[5]     $element[6]\n");
close (Starfile);

#-------move stack to /media and dose weighting----------
#if ($image_num < 9000)	
#{
#	unless (-e "0_shift.txt") {
#		open (Shiftfile,">0_shift.txt");
#		print Shiftfile ("# Unblur shifts file for input stack : ${ctf_a_name}.mrc\n");
#		print Shiftfile ("# Shifts below are given in Angstroms\n");
#		print Shiftfile ("# Number of micrographs: 1\n");
#		print Shiftfile ("# Number of frames per movie: $frame_num\n");
#		print Shiftfile ("# Pixel size (A): $psize\n");
#		print Shiftfile ("# 2 lines per micrograph. 1: X-Shift (A); 2: Y-Shift (A)\n");
#		print Shiftfile ("# -------------------------\n");
#		print Shiftfile ("# Micrograph 1 of 1\n");
#		for (my $i=1;$i <= $frame_num; $i++) {
#			print Shiftfile ("  0.000000   \n");}
#		for (my $j=1;$j <= $frame_num; $j++) {
#	                print Shiftfile ("0.000000   \n");}
#		close(Shiftfile);}
#	open (Dosefile,">${ctf_a_name}_dose");
#	print Dosefile ("${ctf_a_name}_align.mrc\n");
#	print Dosefile ("$frame_num\n");
#	print Dosefile ("${ctf_a_name}_Sumcorr_dose.mrc\n");
#	print Dosefile ("0_shift.txt\n");
#	print Dosefile ("${ctf_a_name}_frc.txt\n");
#	print Dosefile ("1\n");
#	print Dosefile ("$frame_num\n");
#	print Dosefile ("$psize\n");
#	print Dosefile ("yes\n");
#	my $dose_per_frame = $total_dose / $frame_num;
#	print Dosefile ("$dose_per_frame\n");
#	print Dosefile ("$acv\n");
#	print Dosefile ("0.0\n");
#	print Dosefile ("yes\n");
#	close (Dosefile);

#	if (-e "${ctf_a_name}_gSumCorr_DW.mrc") {
#		system "cp ${ctf_a_name}_gSumCorr_DW.mrc ${ctf_a_name}_SumCorr_dose_dis.mrc";}
#--------dose weighting end-------

#--------only for display result------------
#	if ($mode == 2) {
#		system "e2proc2d.py ${ctf_a_name}_Sumcorr_dose.mrc ${ctf_a_name}_test.mrc --meanshrink 10 --process filter.lowpass.gauss:cutoff_freq=0.1 --outmode uint8";
#		system "e2proc2d.py ${ctf_a_name}_test.mrc ${ctf_a_name}_CorrSum.mrc --outmode int16 --outnorescale";
#		system "rm -rf ${ctf_a_name}_test.mrc";
#		if ($phase == 1) {
#			system "e2proc2d.py ${ctf_a_name}_Sumcorr_dose.mrc ${ctf_a_name}_test1.mrc --process math.realtofft --medianshrink 10";
#			system "e2proc2d.py ${ctf_a_name}_test1.mrc ${ctf_a_name}_test2.mrc --process mask.sharp:inner_radius=30:value=0 --outmode uint8";
#			system "e2proc2d.py ${ctf_a_name}_test2.mrc ${ctf_a_name}_CorrFFT.mrc --process mask.sharp:inner_radius=30:value=150  --outmode int16 --outnorescale";}
#		else	{
#			system "e2proc2d.py ${ctf_a_name}_Sumcorr_dose.mrc ${ctf_a_name}_test1.mrc --process math.realtofft --medianshrink 10";
#			system "e2proc2d.py ${ctf_a_name}_test1.mrc ${ctf_a_name}_test2.mrc --process mask.sharp:inner_radius=5:value=0 --outmode uint8";
#			system "e2proc2d.py ${ctf_a_name}_test2.mrc ${ctf_a_name}_CorrFFT.mrc --process mask.sharp:inner_radius=5:value=150  --outmode int16 --outnorescale";}
#		system "rm -rf ${ctf_a_name}_test1.mrc ${ctf_a_name}_test2.mrc";
#		system "e2proc2d.py ${ctf_a_name}_ctf.mrc ${ctf_a_name}_test.mrc --outmode uint8 --clip 400,400";
#		system "e2proc2d.py ${ctf_a_name}_test.mrc ${ctf_a_name}_fitFFT.mrc --outmode int16 --outnorescale";
#		system "rm -rf ${ctftxt_file}_test.mrc";}
#	elsif ($mode == 1) {
#		system "e2proc2d.py ${ctf_a_name}_SumCorr.mrc ${ctf_a_name}_test.mrc --meanshrink 10 --process filter.lowpass.gauss:cutoff_freq=0.1 --outmode uint8";
#        	system "e2proc2d.py ${ctf_a_name}_test.mrc ${ctf_a_name}_CorrSum.mrc --outmode int16 --outnorescale";
#	        system "rm -rf ${ctf_a_name}_test.mrc";
#		system "e2proc2d.py ${ctf_a_name}_SumCorr.mrc ${ctf_a_name}_test1.mrc --process math.realtofft --medianshrink 10";
#		system "e2proc2d.py ${ctf_a_name}_test1.mrc ${ctf_a_name}_test2.mrc --process mask.sharp:inner_radius=5:value=0 --outmode uint8";
#		system "e2proc2d.py ${ctf_a_name}_test2.mrc ${ctf_a_name}_CorrFFT.mrc --process mask.sharp:inner_radius=5:value=150  --outmode int16 --outnorescale";
#		system "rm -rf ${ctf_a_name}_test1.mrc ${ctf_a_name}_test2.mrc";
#		system "e2proc2d.py ${ctf_a_name}_ctf.mrc ${ctf_a_name}_test.mrc --outmode uint8 --clip 400,400";
#		system "e2proc2d.py ${ctf_a_name}_test.mrc ${ctf_a_name}_fitFFT.mrc --outmode int16 --outnorescale";
#		system "rm -rf ${ctf_a_name}_test.mrc";}

#	open (Disfile,">${ctf_a_name}_imod_Log.txt");
#	print Disfile ("UnCorrected FFT: ${ctf_a_name}_fitFFT.mrc\n");
#	print Disfile ("Corrected Sum:   ${ctf_a_name}_CorrSum.mrc\n");
#	print Disfile ("Corrected FFT:   ${ctf_a_name}_CorrFFT.mrc\n\n");
#	将MotionCor2的运动轨迹结果写入_imod_Log.txt文件中
#	my $current_line; my $motion_line;
#	my @Element; my $Element_num; my @real_element;
#	for (my $i=1;$i < $frame_num;$i++) {
#		$current_line = $i + 1;
#		$motion_line = `head -$current_line "${ctf_a_name}_gSumCorr-Full.log" | tail -1`;
#		@Element = split(/\ \ /,$motion_line);
#		$Element_num = scalar @Element;
#		for (my $e=0;$e < $Element_num;$e++) {
#			chomp($Element[$e]);
#			unless ($Element[$e]==0) {
#				@real_element = (@real_element,$Element[$e]);}}
#		print Disfile ("......Shift of Frame #$real_element[1] :  $real_element[2]  $real_element[3]\n");
#		@real_element = "";}
#	close(Disfile);
	#---------only for display result end-----------
	#`cp "${motioncorr_dir}${ctf_a_name}_SumCorr.mrc" "${USB_dir}${ctf_a_name}_SumCorr.mrc"`;
	#`cp "${motioncorr_dir}${ctf_a_name}_SumCorr_DW.mrc" "${USB_dir}${ctf_a_name}_SumCorr_DW.mrc"`;
	#`cp "${ctf_a_name}_SumCorr_ctffind4.log" "${USB_dir}${ctf_a_name}_SumCorr_ctffind4.log"`;
	#`cp "${ctf_a_name}_ctf.mrc" "${USB_dir}${ctf_a_name}_ctf.mrc"`;
	#`rm -rf "${ctf_a_name}.SumCorr.ctf.para"; rm -rf "${ctf_a_name}_ctf_avrot.txt"; rm -rf "${ctf_a_name}_ctf.txt"`;
	#if (-e "${ctf_a_name}.distortion.para"){`rm ${ctf_a_name}.distortion.para`}
	#`rm ${ctf_a_name}_gSumCorr.mrc`;
	#if (-e "${ctf_a_name}_SumCorr_dose_dis.mrc"){`mv "${ctf_a_name}_SumCorr_dose_dis.mrc" "${USB_dir}${ctf_a_name}_SumCorr_dose_dis.mrc"`}
	#unless (-e "${USB_dir}${ctf_a_name}_SumCorr_DW.mrc") {
	#	sleep(15);
	#	if (-e "${ctf_a_name}_SumCorr_DW.mrc"){
	#	`mv "${ctf_a_name}_SumCorr_DW.mrc" "${USB_dir}${ctf_a_name}_SumCorr_doseWeight.mrc"`}}

#summarize stigma every 10 images
#	my $file_name = $ctf_a_name;
#	$file_name =~ s/^${job_name}_//;
#	my $remain = $file_name % 10;
#	if ($remain == 0) {
#		if ($file_name >= 10) {
#			my $last_num = $file_name;
#			my $first_num = $last_num - 10 + 1;
#			`cd $ctf_dir; Stigma_check_hxj_v1.pl -input_file $ctf_values -job $job_name -first_num $first_num -last_num $last_num >> ${ctf_a_name}_auto_f3_ctf.log &`;
#			print "cd $ctf_dir; Stigma_check_hxj_v1.pl -input_file $ctf_values -job $job_name -first_num $first_num -last_num $last_num >> ${ctf_a_name}_auto_f3_ctf.log &";
#			my $disk_space_line = `df -h | grep work1`;	
#			my @disk_space = split(/ +/,$disk_space_line);
#			$disk_space[4] =~ s/\%//;
#			open(TMPfile,">>${ctf_values}_stigma");
#			print TMPfile ("The data disk has been used $disk_space[4]%\n");
#			print TMPfile ("Output frame numbers: $frame_num\n");
#			close(TMPfile);
#			$disk_space_line = `df -h | grep work1`;
#			@disk_space = split(/ +/,$disk_space_line);
#			$disk_space[4] =~ s/\%//;
#			open(TMPfile,">>${ctf_values}_stigma");
#			print TMPfile ("USB has been used $disk_space[4]%\n");
#			close(TMPfile);}}
#}
my @usb_string = split /\//, $USB_dir; #从USB路径中提取USB名称
my $USB = "/$usb_string[1]";
my $disk_space_line = `df -h | grep $USB`; #根据USB名称提取USB信息
my @disk_space = split /\s+/, $disk_space_line; #分空格提取
$disk_space[4] =~ s/\%//; #去掉%
my $drift_result;

if (-e "${USB_dir}MotionCorr/${ctf_a_name}-Patch-Full.log") 
{
	$drift_result = `echo ${USB_dir}MotionCorr/${ctf_a_name} | drift_cal.py`;
}

#将时间格式转换为: 2022-07-21T19:09
$mon = sprintf "%02d", $mon;
$day = sprintf "%02d", $day;
$hour = sprintf "%02d", $hour;
$minute = sprintf "%02d", $minute;
#保存需要展示的数据
open(DataFile1, ">>${job_name}_DataFile1.txt");
print DataFile1 ("$year-$mon-${day}T$hour:$minute, $defocus, $stigma, $element[3], $element[4], $element[5], $element[6], $disk_space[4], $drift_result");
close(DataFile1);

open(DataFile1, ">${job_name}_DataFile2.txt");
print DataFile1 ("${USB_dir}, ${ctf_a_name}, ${mode}");
close(DataFile1);

#脚本路径
#my @path_string = split /\//, $ctf_dir;
#my $length = scalar @path_string;
#my $script_dir = "";
#for (my $i=1; $i <= ($length-5) ; $i++) {
#	$script_dir = $script_dir."/".$path_string[$i];}
$t1 = Benchmark->new;
my $td1 = timediff($t1, $t0);
open (TMPfile3,">>${INFO_dir}ctf_timer.log");
print TMPfile3 ("ctffind took:", timestr($td1), "\n");
close (TMPfile3);


chdir $USB_dir;
#自动挑颗粒
`relion_autopick --i CtfFind/micrograph_${num_name}_ctf.star --odir Autopick/ --pickname autopick_${num_name} --LoG  --LoG_diam_min $dmin --LoG_diam_max $dmax --shrink 0 --lowpass 20 --LoG_adjust_threshold 0 --LoG_upper_threshold 5 >> Autopick/${job_name}_auto_picking.txt`;
print "relion_autopick --i CtfFind/micrograph_${num_name}_ctf.star --odir Autopick/ --pickname autopick_${num_name} --LoG  --LoG_diam_min $dmin --LoG_diam_max $dmax --shrink 0 --lowpass 20 --LoG_adjust_threshold 0 --LoG_upper_threshold 5 >> Autopick/${job_name}_auto_picking.txt";

$t2 = Benchmark->new;
my $td2 = timediff($t2, $t1);
open (TMPfile3,">>${INFO_dir}autopicking_timer.log");
print TMPfile3 ("autopicking took: ", timestr($td2), "\n");
close (TMPfile3);

chdir $ctf_dir;
unless (-e "${USB_dir}Display"){`mkdir ${USB_dir}Display`;}
#画四格图
`plot_4.py ${USB_dir} ${ctf_a_name} ${mode}`;

exit;
