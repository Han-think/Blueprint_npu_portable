include<dimensions.scad>;
//MAIN BODY
difference(){
	difference(){
		cylinder(r=mainHousing_r, h=mainHousing_l);
		cylinder(r=mainHousing_ri, h=mainHousing_l);
		
	}
	for ( i = [0:360/finCount:360]){
		translate([0,0,ringThickness]){
			rotate([0,0,i]){
				cube([finThickness, mainHousing_r,finRoot-ringThickness]);
			}
		}
	}
}