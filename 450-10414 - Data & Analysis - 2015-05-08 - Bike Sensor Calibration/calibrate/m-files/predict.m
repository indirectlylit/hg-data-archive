function [h] = optimizeCurrentModel(readings, theta)

% input X is:
%  - a column of ones for the constant term
%  - a column for the readings
m = length(readings);

X = [ones(m, 1) readings'];
h = X * theta;

end
