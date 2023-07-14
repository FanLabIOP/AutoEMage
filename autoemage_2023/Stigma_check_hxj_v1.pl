#!/usr/bin/perl
use Getopt::Long;
use warnings;
use strict;

my $in_file; my $job; my $first_num; my $last_num;
GetOptions(
	'input_file=s' 		=>\$in_file,
	'job=s' 			=>\$job,
	'first_num=i' 		=>\$first_num,
	'last_num=i' 		=>\$last_num);

unless ($in_file && $job && $first_num && $last_num) {
	print "$0 使用方法：\n*必要参数*\t解释\n";
	print "\t-input_file \t输入文件名\n\t-job \t任务名\n";
	print "\t-first_num \t第一张照片数\n\t-last_num \t最后一张照片数\n";
    exit;}
unless (-e $in_file) {print "输入文件不存在!!!"; exit;}

chomp($first_num);
chomp($last_num);
my $stigma_total=0;
my $stigma_angle_total=0;
my $sqr_dev_total=0;
my $defocus_total=0;
my $dose_total=0;
my $total_num = $last_num - $first_num + 1;
my $prefix_num; my $prefix; my $line; my @element;
for (my $i=$first_num; $i <= $last_num; $i++) {
	$prefix_num = sprintf "%04d", $i;
	$prefix = "${job}_$prefix_num";
	$line = `awk '/$prefix/' $in_file | tail -1`;
	@element = split /\t+/, $line;
	$stigma_total = $element[6] + $stigma_total;	
	print "$element[7]\n";
	$element[7] =~ s/^[-]{1}//;
	$stigma_angle_total = $element[7] + $stigma_angle_total;}	

my $stigma_mean = $stigma_total / ( $last_num - $first_num + 1 );
print "Stigma mean: $stigma_mean\n";
my $stigma_angle_mean = $stigma_angle_total / ( $last_num - $first_num + 1 );
print "Angle mean: $stigma_angle_mean\n";

my $angle_mode;
if ($stigma_angle_mean > 45) {$angle_mode = 12;}
else {$angle_mode=14;}
if ($angle_mode==12) {
	$stigma_angle_total=0;
	for (my $i=$first_num; $i <= $last_num; $i++) {
		$prefix_num = sprintf "%04d", $i;
		$prefix = "${job}_$prefix_num";
		$line = `awk '/$prefix/' $in_file | tail -1`;
		@element=split (/\t+/, $line);
		if ($element[7] < 0) {
		print "$element[7]\n";
		$element[7] = 180 + $element[7];}
		$stigma_angle_total = $element[7] + $stigma_angle_total;}
	$stigma_angle_mean = $stigma_angle_total / ( $last_num - $first_num + 1 );
	print "Corrected angle mean: $stigma_angle_mean\n";}
my $defocus_mean;
for (my $i=$first_num; $i <= $last_num; $i++) {
	$prefix_num = sprintf "%04d",$i;
	$prefix = "${job}_$prefix_num";
	$line = `awk '/$prefix/' $in_file | tail -1`;
	@element = split (/\t+/, $line);
	if ($angle_mode==12) {
		if ($element[7] < 0) {$element[7] = 180 + $element[7];}}
	$sqr_dev_total += ( $element[7] - $stigma_angle_mean ) ** 2;
	$defocus_mean = ( $element[4] + $element[5] ) * 0.5;
	$defocus_total += $defocus_mean;
	$dose_total += $element[0];}

my $standard_dev = ( $sqr_dev_total / $total_num ) ** 0.5;
print "Standard deviation of stigma angle: $standard_dev\n";
my $stigma_confidence = ( 1 - $standard_dev / 90 ) * 100;
print "Stigma confidence: $stigma_confidence%\n";
if ($stigma_confidence > 90){
	print "\nPlease eliminate obj stigma!!!\nstigma mean $stigma_mean\nstigma angle $stigma_angle_mean\n"
	}
$defocus_mean = $defocus_total / $total_num;
$defocus_mean = sprintf "%.2f", $defocus_mean;

my $dose_mean = $dose_total / $total_num;
$dose_mean = sprintf "%.2f",$dose_mean;

$stigma_mean = sprintf("%.1f",$stigma_mean);
$stigma_angle_mean = sprintf("%.1f",$stigma_angle_mean);
$standard_dev = sprintf("%.1f",$standard_dev);
$stigma_confidence = sprintf("%.1f",$stigma_confidence);

open(TMPfile,">>${in_file}_stigma");
print TMPfile ("$first_num\t$last_num\t$stigma_mean\t$stigma_angle_mean\t$standard_dev\t$stigma_confidence%\t$defocus_mean\t$dose_mean\n");
close(TMPfile);

exit;

