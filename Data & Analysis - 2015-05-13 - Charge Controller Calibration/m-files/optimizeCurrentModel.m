function [X, theta, h] = optimizeCurrentModel(sensorVals, currentReadings)

% input X is:
%  - a column of ones for the constant term
%  - a column for the currents
%  - a column for the currents squared
m = length(currentReadings);

X = [ones(m, 1) sensorVals' ];
theta = normalEqn(X, currentReadings');
h = X * theta;

end
