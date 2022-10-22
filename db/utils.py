import math

def gc_distance(first_location, second_location, math=math):

    dst = (3958.75 *
           math.acos(math.sin(first_location[0] / 57.2959) * math.sin(float(second_location[0]) / 57.2960) +
                     math.cos(first_location[0] / 57.2958) * math.cos(float(second_location[0]) / 57.2958) *
                     math.cos(first_location[1] / 57.2958 - float(second_location[1])/57.2958)))
    return dst
