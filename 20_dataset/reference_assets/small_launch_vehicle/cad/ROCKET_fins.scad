include<dimensions.scad>;
//FINS (PRINT FINCOUNT)
union(){
	hull(){
		cylinder(r=.01, h=finThickness);
		translate([finRoot,0,0])
		cylinder(r=.01, h=finThickness);
		translate([sqrt(pow(finSweep,2)-pow(finHeight,2)),-finHeight,0])
		cylinder(r=.01, h=finThickness);
	}
	difference(){
		cube([finRoot, mainHousing_r-engineHousingOD/2, finThickness]);
		cube([ringThickness,mainHousing_r-engineHousingOD/2, finThickness]);
	}
}