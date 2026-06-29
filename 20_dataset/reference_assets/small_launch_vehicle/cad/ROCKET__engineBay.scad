include<dimensions.scad>;
//ENGINE BAY
difference(){
	cylinder(r=engineHousingOD/2, h = engineHousingLength);
	cylinder(r=engineHousingID/2, h = engineHousingLength);
}