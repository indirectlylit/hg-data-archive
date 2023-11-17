function [X, theta, h] = optimizeVoltageModel(sensorVals, voltageReadings)

% input X is a column of ones for the constant term and a column for the actual voltages
m = length(voltageReadings)
X = [ones(m, 1) sensorVals'];
theta = normalEqn(X, voltageReadings');
h = X * theta;
whos

end
