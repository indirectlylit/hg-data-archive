function [X, theta, h] = optimizeCurrentModel(c, v, c_meas, v_meas)

m = length(c_meas);

c = c';
v = v';
c_meas = c_meas';
v_meas = v_meas';

% X is:
%  - ones for the constant term
%  - the currents
%  - the currents squared
%  - the voltages
%  - the voltages squared
%  - the currents * the voltages
X = [ones(m, 1) c c.^2 v v.^2 c.*v ];

theta = normalEqn(X, [c_meas.*v_meas]);
h = X * theta;

end
