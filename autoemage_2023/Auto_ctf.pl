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

my $mode; my $INFO_dir; my $USB_dir; my $job_name; my $rmi; 
my $psize; my $total_dose; my $bin; my $acv; my $SpA; my $ac; my $sps; 
my $min_r; my $max_r; my $min_d; my $max_d; my $dss; my $exa; my $phase;
my $min_Pshift; my $max_Pshift; my $PS_step; my $thr; my $space_limit; 
my $stack_size; my $obj_stigma_x; my $obj_stigma_y;
GetOptions(
	'mode=i' 	=>\$mode,
	'USB_dir=s'	=>\$USB_dir,
	'job=s'	=>\$job_name,
	'rmi=i'	=>\$rmi,
	'psize=f' 	=>\$psize,
	'total_dose=f'  =>\$total_dose,
	'bin=i'	=>\$bin,
	'acv=i' 	=>\$acv,
	'SpA=f' 	=>\$SpA,
	'ac=f' 	=>\$ac,
	'sps=f' 	=>\$sps,
	'min_r=f' 	=>\$min_r,
	'max_r=f' 	=>\$max_r,
	'min_d=f' 	=>\$min_d,
	'max_d=f' 	=>\$max_d,
	'dss=f' 	=>\$dss,
	'exa=f' 	=>\$exa,
	'phase=i' 	=>\$phase,
	'min_Pshift=f'  =>\$min_Pshift,
	'max_Pshift=f'  =>\$max_Pshift,
	'PS_step=f' 	=>\$PS_step,
	'thr=i' 	=>\$thr,
	'drive_space=i' =>\$space_limit,
	'stack_size=f'	=>\$stack_size,
	'obj_stigma_x=f'=>\$obj_stigma_x,
	'obj_stigma_y=f'=>\$obj_stigma_y);
        
unless($mode && $job_name && $USB_dir && $psize && $total_dose) 
{
	print "$0 使用方法：\n*必要参数*\t解释\n"; 
	print "\t-mode \t1: 计数; 2: 超高分辨\n";
	print "\t-INFO_dir \t记录文件夹\n";
	print "\t-USB_dir \t目标文件夹\n";
	print "\t-job \t任务名称\n";
	print "\t-psize\t像素尺寸\n";
	print "\t-drive_space\t最大存储容量\n";
	print "[可选参数]\t默认值\t解释\n";
	print "\t-acv\t300.0\t加速电压 (keV)\n";
	print "\t-SpA\t2.7\t球面像差 (mm)\n";
	print "\t-ac\t0.07\t振幅对比度\n";
	print "\t-sps\t512\tSize of power spectrum to compute\n";
	print "\t-min_r\t30.0\t最小分辨率（埃）\n";
	print "\t-max_r\t5.0\t最大分辨率（埃）\n";
	print "\t-min_d\t5000.0\t最小散焦（埃）\n";
	print "\t-max_d\t50000.0\t最大散焦（埃）\n";
	print "\t-dss\t500\t散焦搜索步长\n";
	print "\t-exa\t100\t预期像散\n";
	print "\t-phase\t1\t是否计算额外相位移动？ 1 是; 2 否\n";
	print "\t-min_Pshift\t0.0\t最小相位移动 (radian)\n";
	print "\t-max_Pshift\t3.15\t最大相位移动 (radian)\n";
	print "\t-PS_step\t0.5\t相位移动搜索步长\n";
	print "\t-thr_p\t1\tctffind 线程数\n";
	print "\t-stack_size\tmrcs stack 文件大小 (例如：2080375808)\n";
	print "\t-obj_stigma_x\t0\tthe current objective stigma x value\n";
	print "\t-obj_stigma_y\t0\tthe current objective stigma y value\n";
	exit;
}
	
unless ($acv) {$acv=300.0}
unless ($SpA) {$SpA=1.4}
unless ($ac) {$ac=0.1}	
unless ($sps) {$sps=512}		
unless ($min_r) {$min_r=30.0}		
unless ($max_r) {$max_r=5.0}		
unless ($min_d) {$min_d=5000.0}		
unless ($max_d) {$max_d=50000.0}		
unless ($dss) {$dss=500.0}		
unless ($exa) {$exa=1000.0}		
unless ($phase) {$phase=2}
unless ($min_Pshift) {$min_Pshift=0.0}
unless ($max_Pshift) {$max_Pshift=3.15}
unless ($PS_step) {$PS_step=0.5}
unless ($thr) {$thr=1}
unless ($stack_size) {$stack_size=1140851712}
unless ($obj_stigma_x) {$obj_stigma_x=0}
unless ($obj_stigma_y) {$obj_stigma_y=0}
unless ($bin) {$bin=1}
unless ($space_limit) {$space_limit=97}

sleep(10);
#记录一下当前时间
my ($sec,$min,$hour,$day,$mon,$year,$wday,$yday,$isdst) = localtime();
my $datestring = localtime();
$year = 1900+$year;
$mon = $mon+1;
print "$year-$mon-$day $hour:$min:$sec\n";

$USB_dir = "${USB_dir}${job_name}/";
$INFO_dir = "${USB_dir}INFO/"; #记录文件夹
my $INFO_filename = "${INFO_dir}$job_name";
my $ctf_dir = "${USB_dir}CtfFind/"; #ctf文件夹
my $motioncorr_dir = "${USB_dir}MotionCorr/"; #motioncorr文件夹

#根据电镜模式和像素点大小来确定放大倍数
my $magnification;
if ($mode == 1) {
	if ($psize == 1.35) {$magnification = "EFTEM SA 105kX"}
	elsif ($psize == 1.04) {$magnification = "EFTEM SA 130kX"}
	elsif ($psize == 0.82) {$magnification = "EFTEM SA 165kX"}
	elsif ($psize == 0.65) {$magnification = "EFTEM SA 215kX"}
	elsif ($psize == 0.5) {$magnification = "EFTEM SA 265kX"}
	elsif ($psize == 3.4) {$magnification = "EFTEM SA 42000X"}
	elsif ($psize == 2.73) {$magnification = "EFTEM SA 53000X"}
	elsif ($psize == 1.74) {$magnification = "EFTEM SA 81000X"}
	elsif ($psize == 2.22) {$magnification = "EFTEM SA 64000x"}
	elsif ($psize == 5.42) {$magnification = "EFTEM SA 26000x"}
	elsif ($psize == 4.3) {$magnification = "EFTEM SA 33000x"}
	else {print "无法匹配像素尺寸！！！\n";}}
elsif ($mode == 2) {
	if ($psize == 0.68) {$magnification = "EFTEM SA 105kX"}
	elsif ($psize == 0.88) {$magnification = "EFTEM SA 81000X"}
	elsif ($psize == 1.36) {$magnification = "EFTEM SA 53000X"}
	elsif ($psize == 0.52) {$magnification = "EFTEM SA 130kX"}
	elsif ($psize == 0.41) {$magnification = "EFTEM SA 165kX"}
	elsif ($psize == 0.325) {$magnification = "EFTEM SA 215kX"}
	elsif ($psize == 0.25) {$magnification = "EFTEM SA 215kX"}
	elsif ($psize == 2.71) {$magnification = "EFTEM SA 26000X"}
	elsif ($psize == 1.7) {$magnification = "EFTEM SA 42000X"}
	elsif ($psize == 0.34) {$magnification = ""}
	elsif ($psize == 1.11) {$magnification = "EFTEM SA 64000x"}
	else {print "无法匹配像素尺寸！！！\n";}}
else {print "无法匹配电镜模式！！！\n";}

chdir $motioncorr_dir;

open Tmpfile, ">>${INFO_dir}current_TEMstigma" or die "Open failed: $!";
print Tmpfile ("$obj_stigma_x\t$obj_stigma_y\n");
close Tmpfile;

#提取需要计算ctf的文件
my $ctf_postfix = "_ctf.mrc"; #ctf 文件后缀
my $SumCorr_postfix = "_SumCorr_DW.mrc"; #运动修正后的照片后缀
#my $mrcs_postfix = ".mrcs"; #
#运动修正后的照片名称
my @SumCorr_name = grep {$_ =~ s/$SumCorr_postfix$//} glob ("${job_name}_[0-9][0-9][0-9][0-9]$SumCorr_postfix");
#CTF 文件名称
my @ctf_name = grep {$_ =~ s/$ctf_postfix//} glob ("${job_name}_[0-9][0-9][0-9][0-9]$ctf_postfix");
my $SumCorr_num = scalar @SumCorr_name;
print "已完成运动修正的照片: @SumCorr_name\n";
print "已完成 CTF 计算的照片: @ctf_name\n";
my %CTF;
++$CTF{$_} for @ctf_name;
my @non_ctf_name = grep {--$CTF{$_} < 0} @SumCorr_name; #抓取没有CTF的照片
print "需要 CTF 计算的照片: @non_ctf_name\n";
my $ctf_remain = scalar @non_ctf_name;
print "$ctf_remain tasks remain...\n";
undef %CTF;
++$CTF{$_} for @SumCorr_name;

my $pixelsize = sprintf "%.6f", $psize;
my $voltage = sprintf "%.6f", $acv;
my $sphe_abber = sprintf "%.6f", $SpA;
my $amp_contrast = sprintf "%.6f", $ac;
my $binning_pz;
if ($mode==1) {$binning_pz = sprintf "%.6f", $psize;}
else {$binning_pz = sprintf "%.6f", $psize*2;} #超分辨模式下，binfactor=2

my $ctf_a_name; my $SumCorr_mrc; my $show_ctf_remain; 
my $line; my @element;
my $count = 1;
my $num_end; my $num_start; my $remain; my $tens;

while (1) 
{
	if ($ctf_remain <= 0) 
	{
		sleep(30);
		undef @non_ctf_name;
		@SumCorr_name = grep {$_ =~ s/$SumCorr_postfix$//} glob ("${job_name}_[0-9][0-9][0-9][0-9]$SumCorr_postfix");
		@non_ctf_name = grep {--$CTF{$_} < 0} @SumCorr_name;
		$ctf_remain = scalar @non_ctf_name;
		print "需要计算 CTF 的照片名: @non_ctf_name\n";
		print "$ctf_remain tasks remain...\n";
		undef %CTF;
		++$CTF{$_} for @SumCorr_name;
	}
	else 
	{
		my ($sec,$min,$hour,$day,$mon,$year,$wday,$yday,$isdst) = localtime();
		$year = 1900+$year;
		$mon = $mon+1;
		print "$year-$mon-$day $hour:$min:$sec\n";
		$ctf_a_name = shift(@non_ctf_name);
		$SumCorr_mrc = "${ctf_a_name}$SumCorr_postfix";
		sleep(1);
		system "cp $SumCorr_mrc ${ctf_dir}$SumCorr_mrc"; 
		sleep(1);
		if (-e $SumCorr_mrc) {				
			$show_ctf_remain = $ctf_remain-1;
			print "The number of images waiting: $show_ctf_remain\n";
			print "CTFFIND is working on $SumCorr_mrc\n";
			$line = `tail -1 ${INFO_dir}current_TEMstigma`;
			@element = split (/\t+/, $line);
			$obj_stigma_x = $element[0];
			chomp($element[1]);
			$obj_stigma_y = $element[1];
			$remain = $count % 10;
			if ($remain == 1) {
				#生成 .star 文件以便 relion 执行 generating a .star file for using relion
				$tens = $count/10;
				$tens =~ s/\.[0-9]//;
				if ($tens != 0) {`cp "${ctf_dir}micrographs_${num_start}to${num_end}_ctf.star" "${INFO_dir}micrographs_${num_start}to${num_end}_ctf.star"`;}
				$num_end = ($tens+1)*10;
				$num_start = $num_end - 9;
				open (Starfile, ">${ctf_dir}micrographs_${num_start}to${num_end}_ctf.star");
				print Starfile ("\n# version 30001\n\ndata_optics\n\nloop_\n_rlnOpticsGroupName #1\n_rlnOpticsGroup #2\n");
				print Starfile ("_rlnMicrographOriginalPixelSize #3\n_rlnVoltage #4\n_rlnSphericalAberration #5\n");
				print Starfile ("_rlnAmplitudeContrast #6\n_rlnMicrographPixelSize #7\n");
				print Starfile ("opticsGroup1            1     $pixelsize   $voltage     $sphe_abber     $amp_contrast     $binning_pz\n\n\n");
				print Starfile ("# version 30001\n\ndata_micrographs\n\nloop_\n_rlnMicrographName #1\n_rlnOpticsGroup #2\n");
				print Starfile ("_rlnCtfImage #3\n_rlnDefocusU #4\n_rlnDefocusV #5\n_rlnCtfAstigmatism #6\n");
				print Starfile ("_rlnDefocusAngle #7\n_rlnCtfFigureOfMerit #8\n_rlnCtfMaxResolution #9\n");
				close (Starfile);}
				unless (-e "${USB_dir}Class2D/run${num_start}to${num_end}"){`mkdir ${USB_dir}Class2D/run${num_start}to${num_end}`;}
			print "Auto_ctf_find.pl -mode $mode -job $job_name -INFO_dir $INFO_dir -USB_dir $USB_dir -rmi $rmi -psize $psize -total_dose $total_dose -bin $bin -acv $acv -SpA $SpA -ac $ac -sps $sps -min_r $min_r -max_r $max_r -min_d $min_d -max_d $max_d -dss $dss -exa $exa -phase $phase -min_Pshift $min_Pshift -max_Pshift $max_Pshift -PS_step $PS_step -thr $thr -ctf_a_name $ctf_a_name -drive_space $space_limit -stack_size $stack_size -obj_stigma_x $obj_stigma_x -obj_stigma_y $obj_stigma_y -y $year -mon $mon -day $day -h $hour -m $min -file_num $num_end >> ${INFO_filename}_auto_ctf_find.log &\n";	
			`Auto_ctf_find.pl -mode $mode -job $job_name -INFO_dir $INFO_dir -USB_dir $USB_dir -rmi $rmi -psize $psize -total_dose $total_dose -bin $bin -acv $acv -SpA $SpA -ac $ac -sps $sps -min_r $min_r -max_r $max_r -min_d $min_d -max_d $max_d -dss $dss -exa $exa -phase $phase -min_Pshift $min_Pshift -max_Pshift $max_Pshift -PS_step $PS_step -thr $thr -ctf_a_name $ctf_a_name -drive_space $space_limit -stack_size $stack_size -obj_stigma_x $obj_stigma_x -obj_stigma_y $obj_stigma_y -y $year -mon $mon -day $day -h $hour -m $min -file_num $num_end >>${INFO_filename}_auto_ctf_find.log &`;				
			$ctf_remain--; $count++}
		sleep(5);
	}
}
exit;
