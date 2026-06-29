include<dimensions.scad>;
difference(){
	cylinder(r=mainHousing_ri, h = ringThickness);
	cylinder(r=engineHousingOD/2, h = ringThickness);
	for ( i = [0:360/ringRibCount:360]){
		rotate([0,0,i]){
			translate([engineHousingOD/2+((mainHousing_ri*2)-engineHousingOD)/4,0,0]){
				cylinder(r=ringRibOD/2, h = ringThickness+10);
			}
		}
	}
}
