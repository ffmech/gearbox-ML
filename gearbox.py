import math
import sympy

class Gear:
    def __init__(self, teeth=None, DP=None, pitch_diameter=None, helix_angle_deg=15, pressure_angle_deg=20, rpm=100, power=10):
        #self.z = teeth
        #self.DP = DP
        self.rpm = rpm
        self.power = power
        self.beta = math.radians(helix_angle_deg)
        self.phi = math.radians(pressure_angle_deg)

        # Count how many inputs are provided
        provided = sum(x is not None for x in [teeth, DP, pitch_diameter])
        if provided < 2:
            raise ValueError("Provide at least two of: teeth, DP, pitch_diameter")
        
        # Calculate the missing one
        if teeth is None:
            self.z = int(round(pitch_diameter * DP * math.cos(self.beta)))
        else:
            self.z = teeth
            
        if DP is None:
            self.DP = self.z / (pitch_diameter * math.cos(self.beta))
        else:
            self.DP = DP
            
        if pitch_diameter is None:
            self.pitch_diameter_val = self.z / (self.DP * math.cos(self.beta))
        else:
            self.pitch_diameter_val = pitch_diameter

    @property
    def pitch_diameter(self):
        return self.z / (self.DP * math.cos(self.beta))

    # Method: create mating gear from ratio
    def mate_for_ratio(self, ratio: float):
        """
        Create a new Gear that meshes with self, 
        given the desired ratio (gear_teeth / pinion_teeth).
        """
        new_teeth = int(round(self.z * ratio))
        return Gear(new_teeth, self.DP, helix_angle_deg=math.degrees(self.beta), 
                    pressure_angle_deg=math.degrees(self.phi))

    def load_calculation(self):
        self.pitch_line_speed = (math.pi*self.DP*self.rpm)/12
        self.tangential_force = 33000*(self.power/self.pitch_line_speed)
        self.axial_load = self.tangential_force*math.tan(self.phi)
        self.radial_load = self.tangential_force*(math.tan(self.beta)/math.cos(self.phi))

        return {
                    "Pitch line speed": self.pitch_line_speed,
                    "Tangential Force": self.tangential_force,
                    "Axial Load": self.axial_load,
                    "Radial Load": self.radial_load
                }

    def __mul__(self, other):
        if not isinstance(other, Gear):
            raise TypeError("Can only multiply Gear by Gear")
        if self.DP != other.DP:
            raise ValueError(f"Cannot mesh gears with different DP: {self.DP} vs {other.DP}")
        if self.rpm is None:
            raise ValueError("Driving gear RPM must be set before pairing")
        # Overwrite the second gear's RPM based on the first gear and the ratio
        #other.rpm = self.rpm / (other.z / self.z)
        return GearPair(self, other)


class GearPair:
    def __init__(self, pinion: Gear, gear: Gear):
        self.pinion = pinion
        self.gear = gear
        self.input_speed = self.pinion.rpm
        self.input_power = self.pinion.power
    
    @property
    def ratio(self):
        return self.gear.z / self.pinion.z
    
    @property
    def center_distance(self):
        return 0.5 * (self.pinion.pitch_diameter + self.gear.pitch_diameter)
    
    @property
    def input_torque_inlbf(self):
        return 63025 * self.input_power / self.input_speed
    
    @property
    def output_speed_rpm(self):
        return self.input_speed / self.ratio
    
    @property
    def output_torque_inlbf(self):
        return self.input_torque_inlbf * self.ratio
    
    #@property
    #def pitch_line_speed(self):
    #    return (math.pi*self.DP*self.input_speed)/12

    def summary(self):
        return {
            "ratio": round(self.ratio, 2),
            "center_distance_in": round(self.center_distance, 3),
            "output_speed_rpm": round(self.output_speed_rpm, 1),
            "output_torque_inlbf": round(self.output_torque_inlbf, 1)
        }


if __name__ == "__main__":
    print("This code runs only when the script is executed directly.")
    pinion = Gear(teeth=120, DP=6, helix_angle_deg=20, rpm=2000, power=20)
    gear = Gear(teeth=20, DP=6,helix_angle_deg=-20)
    #stage0 = pinion*pinion.mate_for_ratio(100)
    #print(stage0.summary())
    stage1 = gear*pinion
    print(stage1.summary())
    print(pinion.load_calculation())
    #new_gear = Gear(P_hp=10, N1_rpm=1800, ratio=6, DP=6, beta_deg=20)
    #print(new_gear.basic_helical())