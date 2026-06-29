include<dimensions.scad>;
//SUB FINS (PRINT SUBCOUNT)
hull(){
	cylinder(r=.01, h=subThickness);
	translate([subRoot,0,0])
	cylinder(r=.01, h=subThickness);
	translate([sqrt(pow(subSweep,2)-pow(subHeight,2)),-subHeight,0])
	cylinder(r=.01, h=subThickness);
	translate([sqrt(pow(subSweep,2)-pow(subHeight,2))+subTip,-subHeight,0])
	cylinder(r=.01, h=subThickness);
}