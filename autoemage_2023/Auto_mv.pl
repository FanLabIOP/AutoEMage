#!/usr/bin/perl
####################################################################################
#Author: Yuanhao Cheng, Wei Ding
#Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
#Created time: 2022/06/16
#Last Edit: 2023/08/24
#Group: SM6, The Institute of Physics, Chinese Academy of Sciences
####################################################################################
use strict;
use warnings;
use Getopt::Long;

my $mode; my $EM_dir; my $USB_dir; my $INFO_dir; my $job_name;
my $raw_n; my $drive_space; my $rmi; my $stack_size; my $psize; my $total_dose;
my $acv; my $gain_file; my $name; my $collection_mode;

GetOptions(
	'mode=i' 				=>\$mode, #电镜模式
	'EM_dir=s' 				=>\$EM_dir, #电镜文件夹
	'USB_dir=s'				=>\$USB_dir, #目标文件夹
	'INFO_dir=s'			=>\$INFO_dir,
	'job=s'					=>\$job_name, #转移后的文件命名
	'raw_num=i'				=>\$raw_n,
	'rmi=i'					=>\$rmi,
	'stack_size=f'			=>\$stack_size,
	'drive_space=i' 		=>\$drive_space, #硬盘允许存储的最大容量（超过该数值则无法转移）
	'psize=f' 				=>\$psize,
	'total_dose=f'			=>\$total_dose,
	'gain_file=s' 			=>\$gain_file,
	'name=s' 				=>\$name,
	'acv=i' 				=>\$acv, #加速电压
	'collection_mode=i' 	=>\$collection_mode); #收集软件

unless($mode && $EM_dir && $USB_dir && $job_name && $raw_n && $rmi && $psize && $total_dose) 
{
	print "$0 使用方法：\n*必要参数*\t解释\n"; 
	print "\t-mode \t1: 计数; 2: 超高分辨\n";
	print "\t-INFO_dir \t记录文件夹\n";
	print "\t-USB_dir \t目标文件夹\n\t-EM_dir \t电镜文件夹\n";
	print "\t-job \t任务名称\n";
	print "\t-psize \t像素尺寸\n";
	print "\t-rmi \t1: 转移文件至硬盘; 2: 不转移\n";
	print "\t-raw_n \t初始编号\n";
	print "[可选参数]\t默认值\t解释\n";
	print "\t-stack_size\tmrcs stack 文件大小 (例如：2080375808)\n";
	print "\t-drive_space\t90%\t硬盘最大储存容量比例\n";
	exit;
}

unless($drive_space) {$drive_space=97}
unless($stack_size) {$stack_size=100536940}
unless($acv) {$acv=300.0}

#创建必要的文件夹
$USB_dir = "${USB_dir}${job_name}/";
unless (-e "${USB_dir}INFO"){`mkdir ${USB_dir}INFO`;}
$INFO_dir = "${USB_dir}INFO/"; #记录文件夹
unless (-e "${USB_dir}CtfFind"){`mkdir ${USB_dir}CtfFind`;}
my $ctf_dir = "${USB_dir}CtfFind/"; #ctf文件夹
unless (-e "${USB_dir}MotionCorr"){`mkdir ${USB_dir}MotionCorr`;}
my $motioncorr_dir = "${USB_dir}MotionCorr/"; #motioncorr文件夹
unless (-e "${USB_dir}Extract"){`mkdir ${USB_dir}Extract`;}
unless (-e "${USB_dir}Autopick"){`mkdir ${USB_dir}Autopick`;}
unless (-e "${USB_dir}Class2D"){`mkdir ${USB_dir}Class2D`;}
unless (-e "${USB_dir}Outliers"){`mkdir ${USB_dir}Outliers`;}
unless (-e "${USB_dir}Select"){`mkdir ${USB_dir}Select`;}
unless (-e "${USB_dir}InitialModel"){`mkdir ${USB_dir}InitialModel`;}

#sleep(30);

#记录一下当前时间
my ($sec,$min,$hour,$day,$mon,$year,$wday,$yday,$isdst) = localtime();
my $datestring = localtime();
$year = 1900+$year;
$mon = $mon+1;
print "$year-$mon-$day $hour:$min:$sec\n";

chdir $EM_dir;
#-----gain process-----
if ($gain_file =~ /\.dm4/) 
{ 
	system "dm2mrc ${gain_file} ${USB_dir}gain_8bit.mrc";
	print "将 dm4 文件转换为 mrc 文件\n";
}
if (-e "${USB_dir}gain.mrc") 
{
        print "目标文件夹中存在 gain 文件，我们将其重命名为${year}${mon}${day}_${hour}-${min}-${sec}.mrc\n";
	#将已有的 gain 文件重命名
        system "mv ${USB_dir}gain.mrc ${USB_dir}gain_${year}${mon}${day}_${hour}-${min}-${sec}.mrc";
}
if ($gain_file =~ /\.mrc/) 
{ 
	system "cp ${gain_file} ${USB_dir}gain_8bit.mrc"; #复制 gain 文件
	print "复制 gain.mrc\n";
}
#-----gain process end-----

my @name_array = split /\./, $name;
my $file_postfix = ".$name_array[-1]"; #初始照片文件的后缀
my $INFO_record = "${INFO_dir}${job_name}_file_record";

if ($collection_mode == 1) 
{
	#抓取GridSquare文件夹
	my @squares = glob "${EM_dir}Images-Disc1/GridSquare_*";
	my $square_num = scalar @squares;
	my $square_num_old = 0;

	while ($square_num <= 0) 
	{
		print "No gridsquare folder has been created. Wait for 10 seconds\n";
		sleep(10);
		@squares = glob "${EM_dir}Images-Disc1/GridSquare_*";
		$square_num = scalar @squares;
	}

	#抓取GridSquare/Data文件夹
	my @new_grids = glob "${EM_dir}Images-Disc1/GridSquare_*/Data"; 
	my $grids_num_new = scalar @new_grids;

	#重复抓取，直到有文件夹产生
	while ($grids_num_new <= 0) 
	{
		print "No data has been collected. Wait for 5 seconds\n";
		sleep(5);
		@new_grids = glob "${EM_dir}Images-Disc1/GridSquare_*/Data";
		$grids_num_new = scalar @new_grids;
	}

	my @old_grids;
	my $grids_num_old;
	my %diff_dir;
	@diff_dir{@new_grids} = @new_grids;
	delete @diff_dir{@old_grids};
	@new_grids = (keys %diff_dir);
	$grids_num_new = scalar @new_grids;
	print "$grids_num_new folder(s) of data are found.\n";

	my $count = 0;

	while ($square_num_old < $square_num) 
	{
		for (my $i = 0; $i < $grids_num_new; $i++) 
		{
			#从GridSquare/Data文件夹中找fraction.tiff文件
			my $new_folder = $new_grids[$i];
			my @new_stacks = glob "${new_folder}/$name"; 
			my $stacks_num_new = scalar @new_stacks;

			#重复抓取
			while ($stacks_num_new <= 0) 
			{
				sleep(5);
				print "No image exists! Wait for 5 seconds.\n";
				@new_stacks = glob "${new_folder}/$name"; 
				$stacks_num_new = scalar @new_stacks;
			}
			my @old_stacks;
			my $stacks_num_old;
			my %diff_stacks;
			@diff_stacks{@new_stacks} = @new_stacks;
			delete @diff_stacks{@old_stacks};
			@new_stacks = (keys %diff_stacks);
			$stacks_num_new = scalar @new_stacks;
			print "$stacks_num_new image(s) are found in ${new_folder}.\n";

			for (my $k = 0; $k < $stacks_num_new; $k++) 
			{
				my $new_file = $new_stacks[$k]; #取出抓取后的照片
				print "Task $k: transferring $new_file\n";
				#检查目前是否有Auto_mv_corr在运行
				my $dr_running_job = `ps au | grep Auto_mv_corr | grep -v grep | grep -v vim | grep -v gedit |wc -l`; 
		    	chomp($dr_running_job);
				my $dr_thr_remain = 1 - $dr_running_job; #空闲GPU数量

				while ($dr_thr_remain <= 0) 
				{
					sleep(10);
					print "GPU is in use! Wait for 10 seconds.\n";
					$dr_running_job = `ps au | grep Auto_mv_corr | grep -v grep | grep -v vim | grep -v gedit |wc -l`; 
		    		chomp($dr_running_job);
					$dr_thr_remain = 1 - $dr_running_job; #空闲GPU数量
				}
				#如果硬盘存储空间较小，则停止转移
				my @usb_string = split /\//, $USB_dir; #从USB路径中提取USB名称
				my $USB = "/$usb_string[1]";
				my $disk_space_line = `df -h | grep $USB`; #根据USB名称提取USB信息
				my @disk_space = split /\s+/, $disk_space_line; #分空格提取
				$disk_space[4] =~ s/\%//; #去掉%

				if ($disk_space[4] >= $drive_space) 
				{
					print "Disk is full. Please select another disk and restart the task.";
					exit;
				}
				else    {print "Disk used $disk_space[4]%, with $disk_space[3] left\n";}

				my $diskspace = "$disk_space[4]";
				my $new_end_size;

				for (my $l = 0; $l <= 300; $l++) 
				{
					my $new_file_string = `du -b $new_file`;
					my @string_array = split /\s+/, $new_file_string;
					my $new_start_size = $string_array[0];
					
					#确认文件大小不为零
					while ($new_start_size == 0) 
					{
						sleep(5);
						$new_file_string = `du -b $new_file`;
						@string_array = split /\s+/, $new_file_string;
						$new_start_size = $string_array[0];
					}

					$new_file_string = `du -b $new_file`;
					@string_array = split /\s+/, $new_file_string;
					$new_end_size = $string_array[0];

					#确认文件已经写入完毕
					if ($new_start_size == $new_end_size) {last;}
				}

				$count++;
				if ($new_end_size <= $stack_size) 
				{
					print "Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix >> ${INFO_dir}${job_name}_auto_mv_corr.log & \n";
					`Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -INFO_dir $INFO_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix  >> ${INFO_dir}${job_name}_auto_mv_corr.log &`;
				}
				else 
				{
					print "Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix >> ${INFO_dir}${job_name}_auto_mv_corr.log\n";
					`Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -INFO_dir $INFO_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix  >> ${INFO_dir}${job_name}_auto_mv_corr.log &`;
				}
				push @old_stacks, $new_file; #记录转移过的照片
				$stacks_num_old = scalar @old_stacks;
				
				#当前抓取的照片传输完成时，再次抓取
				if ($k == ($stacks_num_new - 1))
				{
					@new_stacks = glob "${new_folder}/$name"; 
					$stacks_num_new = scalar @new_stacks;
					@new_grids = glob "${EM_dir}Images-Disc1/GridSquare_*/Data"; 
					my $grids_num_new_2 = scalar @new_grids;
					#如果当前文件夹有新照片
					if ($stacks_num_new > $stacks_num_old)
					{
						print "New images are found in $new_folder\n";
						@diff_stacks{@new_stacks} = @new_stacks;
						delete @diff_stacks{@old_stacks};
						@new_stacks = (keys %diff_stacks);
						$stacks_num_new = scalar @new_stacks;
						$k = 0;
					}
					#如果发现其他GridSquare/Data文件夹中出现，则说明当前GridSquare数据收集完毕
					elsif ($grids_num_new_2 > $grids_num_new)
					{
						push @old_grids, $new_folder; #记录转移过的文件夹
						$grids_num_old = scalar @old_grids;
						$square_num_old++;
						@diff_dir{@new_grids} = @new_grids;
						delete @diff_dir{@old_grids};
						@new_grids = (keys %diff_dir);
						$grids_num_new = scalar @new_grids;
						$i = 0;
						print "Data transferring complete: $new_folder\n";
						last;
					}
					else
					{
		    			print "No image is found. Wait for 30 seconds.\n";
						sleep(30);
						@new_stacks = glob "${new_folder}/$name";
						@diff_stacks{@new_stacks} = @new_stacks;
						delete @diff_stacks{@old_stacks};
						@new_stacks = (keys %diff_stacks);
						$stacks_num_new = scalar @new_stacks;
						$k = 0;
					}
				}
			}
			$square_num_old++;
		}

	}
}
else
{
	my $count = 0;
	my @new_stacks = glob "${EM_dir}/$name"; 
	my $stacks_num_new = scalar @new_stacks;
	#重复抓取
	while ($stacks_num_new <= 0) 
	{
		sleep(5);
		print "No image exists! Wait for 5 seconds.\n";
		@new_stacks = glob "${EM_dir}/$name"; 
		$stacks_num_new = scalar @new_stacks;
	}
	my @old_stacks;
	my $stacks_num_old;
	my %diff_stacks;
	@diff_stacks{@new_stacks} = @new_stacks;
	delete @diff_stacks{@old_stacks};
	@new_stacks = (keys %diff_stacks);
	$stacks_num_new = scalar @new_stacks;
	print "$stacks_num_new image(s) are found in ${EM_dir}.\n";

	for (my $k = 0; $k < $stacks_num_new; $k++) 
	{
		my $new_file = $new_stacks[$k]; #取出抓取后的照片
		print "Task $k: transferring $new_file\n";
		#检查目前是否有Auto_mv_corr在运行
		my $dr_running_job = `ps au | grep Auto_mv_corr | grep -v grep | grep -v vim | grep -v gedit |wc -l`; 
    	chomp($dr_running_job);
		my $dr_thr_remain = 1 - $dr_running_job; #空闲GPU数量

		while ($dr_thr_remain <= 0) 
		{
			sleep(10);
			print "GPU is in use! Wait for 10 seconds.\n";
			$dr_running_job = `ps au | grep Auto_mv_corr | grep -v grep | grep -v vim | grep -v gedit |wc -l`; 
    		chomp($dr_running_job);
			$dr_thr_remain = 1 - $dr_running_job; #空闲GPU数量
		}
		#如果硬盘存储空间较小，则停止转移
		my @usb_string = split /\//, $USB_dir; #从USB路径中提取USB名称
		my $USB = "/$usb_string[1]";
		my $disk_space_line = `df -h | grep $USB`; #根据USB名称提取USB信息
		my @disk_space = split /\s+/, $disk_space_line; #分空格提取
		$disk_space[4] =~ s/\%//; #去掉%

		if ($disk_space[4] >= $drive_space) 
		{
			print "Disk is full. Please select another disk and restart the task.";
			exit;
		}
		else    {print "Disk used $disk_space[4]%, with $disk_space[3] left\n";}

		my $diskspace = "$disk_space[4]";
		my $new_end_size;

		for (my $l = 0; $l <= 300; $l++) 
		{
			my $new_file_string = `du -b $new_file`;
			my @string_array = split /\s+/, $new_file_string;
			my $new_start_size = $string_array[0];
			
			#确认文件大小不为零
			while ($new_start_size == 0) 
			{
				sleep(5);
				$new_file_string = `du -b $new_file`;
				@string_array = split /\s+/, $new_file_string;
				$new_start_size = $string_array[0];
			}

			$new_file_string = `du -b $new_file`;
			@string_array = split /\s+/, $new_file_string;
			$new_end_size = $string_array[0];

			#确认文件已经写入完毕
			if ($new_start_size == $new_end_size) {last;}
		}

		$count++;
		if ($new_end_size <= $stack_size) 
		{
			print "Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix >> ${INFO_dir}${job_name}_auto_mv_corr.log & \n";
			`Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -INFO_dir $INFO_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix  >> ${INFO_dir}${job_name}_auto_mv_corr.log &`;
		}
		else 
		{
			print "Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix >> ${INFO_dir}${job_name}_auto_mv_corr.log\n";
			`Auto_mv_corr.pl -mode $mode -EM_dir $EM_dir -USB_dir $USB_dir -INFO_dir $INFO_dir -job $job_name -raw_num $count -rename_file $new_file -disk_space $diskspace -psize $psize -total_dose $total_dose -rmi $rmi -acv $acv -postfix $file_postfix  >> ${INFO_dir}${job_name}_auto_mv_corr.log &`;
		}
		push @old_stacks, $new_file; #记录转移过的照片
		$stacks_num_old = scalar @old_stacks;
		
		#当前抓取的照片传输完成时，再次抓取
		if ($k == ($stacks_num_new - 1))
		{
			@new_stacks = glob "${EM_dir}/$name"; 
			$stacks_num_new = scalar @new_stacks;
			#如果当前文件夹有新照片
			if ($stacks_num_new > $stacks_num_old)
			{
				print "New images are found in $EM_dir\n";
				@diff_stacks{@new_stacks} = @new_stacks;
				delete @diff_stacks{@old_stacks};
				@new_stacks = (keys %diff_stacks);
				$stacks_num_new = scalar @new_stacks;
				$k = 0;
			}
			else
			{
    			print "No image is found. Wait for 30 seconds.\n";
				sleep(30);
				@new_stacks = glob "${EM_dir}/$name";
				@diff_stacks{@new_stacks} = @new_stacks;
				delete @diff_stacks{@old_stacks};
				@new_stacks = (keys %diff_stacks);
				$stacks_num_new = scalar @new_stacks;
				$k = 0;
			}
		}
	}
}
exit;
