function [X, theta, h] = optimizeLinearModel(sensor, measured)

m = length(measured)
X = [ones(m, 1) sensor'];
theta = normalEqn(X, measured');
h = X * theta;

end
