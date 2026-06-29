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
//RINGS (PRINT 2)
difference(){
	cylinder(r=ringOD/2, h=ringThickness);
	cylinder(r=ringID/2, h =ringThickness);
}
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
//ENGINE BAY
difference(){
	cylinder(r=engineHousingOD/2, h = engineHousingLength);
	cylinder(r=engineHousingID/2, h = engineHousingLength);
}
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
//SUB FINS (PRINT SUBCOUNT)
hull(){
	cylinder(r=.01, h=subThickness);
	translate([subRoot,0,0])
	cylinder(r=.01, h=subThickness);
	translate([sqrt(pow(subSweep,2)-pow(subHeight,2)),-subHeight,0])
	cylinder(r=.01, h=subThickness);
}