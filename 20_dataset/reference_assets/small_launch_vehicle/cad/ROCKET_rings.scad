include<dimensions.scad>;
//RINGS (PRINT 2)
difference(){
	cylinder(r=mainHousing_ri, h =ringThickness);
	cylinder(r=engineHousingOD/2, h=ringThickness);
}