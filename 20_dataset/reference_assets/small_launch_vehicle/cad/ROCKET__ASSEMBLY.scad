rotate([90,50,0])
difference(){
	union(){
		//Assembly
		include<dimensions.scad>;
		import("STL/engineBay.stl");
		for ( i = [0:360/finCount:360]){
			rotate([0,0,i]){
				translate([finThickness/2,-mainHousing_r,0]){
					rotate([0,-90,0]){
						import("STL/fins.stl");
					}
				}
			}
		}
		import("STL/rings.stl");
		translate([0,0,finRoot]){
			import("STL/rings.stl");
		}
		rotate([0,0,(360/finCount)/2])
		import("STL/mainBody.stl");

		for ( i = [0:360/subCount:360]){
			rotate([0,0,i]){
				translate([subThickness/2,-mainHousing_r,subPosition+subRoot]){
					rotate([0,90,0]){
						import("STL/subFins.stl");
					}
				}
			}
		}
		translate([0,0,mainHousing_l]){
			import("STL/noseCone.stl");
		}
	}
	cube([1000,1000,1000]);
}