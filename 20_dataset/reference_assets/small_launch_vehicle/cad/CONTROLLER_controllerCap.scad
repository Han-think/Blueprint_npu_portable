$fn = 45;
lip=5;
difference(){
	union(){
		translate([0,0,lip]){
			cylinder(r=26.3/2, h=19.63);
		}
		cylinder(r=32.5/2, h=lip);
	}
	translate([0,-6.3,7]){
		cube([13,6.3,14], center = true);
	}
	translate([0,6.3,7]){
		cube([13,6.3,14], center = true);
	}
	translate([0,6.3,24.63/2+lip]){
		cube([3.175,10,19.63+lip], center = true);
	}
	translate([0,-6.3,24.63/2+lip]){
		cube([3.175,10,19.63+lip], center=true);
	}
	rotate([0,90,0]){
		translate([-20,6.3,-5]){
			cylinder(r=5/2, h=100);
		}
	}
	rotate([0,90,0]){
		translate([-20,-6.3,-5]){
			cylinder(r=5/2, h=100);
		}
	}
}