function [all_sensors] = concatenate(sensor_1, sensor_2, sensor_3)

all_sensors = [
				sensor_1(:, [1, 2, 5, 6]);
				sensor_2(:, [1, 3, 5, 6]);
				sensor_3(:, [1, 4, 5, 6]);
			];

end
