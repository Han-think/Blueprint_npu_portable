include<dimensions.scad>;
//NOSE CONE
union(){
	difference(){
		scale([mainHousing_r, mainHousing_r, noseHeight]){
			rotate_extrude(){
				intersection(){
					circle(r=1);
					square(1);
				}
			}
		}
		scale([(mainHousing_r-noseThickness), (mainHousing_r-noseThickness), (noseHeight-noseThickness)]){
			rotate_extrude(){
				intersection(){
					circle(r=1);
					square(1);
				}
			}
		}
	}
	difference(){
		cylinder(r=mainHousing_r/2, h=noseThickness);
		cylinder(r=mainHousing_ri, h=noseThickness);
	}
	translate([0,0,-noseShoulderLength]){
		difference(){
			cylinder(r=mainHousing_ri, h=noseShoulderLength);
			cylinder(r=mainHousing_ri-noseThickness, h=noseShoulderLength);
		}
	}
}