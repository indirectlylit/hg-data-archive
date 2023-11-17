function [X, theta, h] = optimizePowerModel2(v, c, measuredPower)

m = length(measuredPower);

X = [ones(m, 1) (v.*c)'];

theta = normalEqn(X, measuredPower');
h = X * theta;

end
