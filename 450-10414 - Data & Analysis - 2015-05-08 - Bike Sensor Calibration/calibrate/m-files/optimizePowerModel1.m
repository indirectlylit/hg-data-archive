function [X, theta, h] = optimizePowerModel1(v, c, measuredPower)

m = length(measuredPower);

X = [ones(m, 1) (v.*c)' c' v'];
whos


theta = normalEqn(X, measuredPower');
h = X * theta;

end
