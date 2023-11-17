function [X, theta, h] = optimizeCurrentModel(sensorVals, currentReadings)

% X is:
%  - a column of ones for the constant term
%  - a column for the currents
m = length(currentReadings);

X = [ones(m, 1) sensorVals' ];

theta = normalEqn(X, currentReadings');
h = X * theta;

end
