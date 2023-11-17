%% AC Sensor Calibration
clear; close all;

% In these vectors, the first column is from the
% multimeters and the second is sensors.
current = load('current.tsv');
voltage = load('voltage.tsv');

% these are the sensor values
c = current(:,2);
v = voltage(:,2);
p = c .* v;

% This is the actual power as measured by the multimeters
y = current(:,1) .* voltage(:,1);

% Number of samples
m = length(y);

% set up plot
colordef 'black';
plot(y, y-y, '-y');
hold on;
title('Error in Estimated Power');
xlabel('Actual Measured Power (W)');
ylabel('Estimate Error (W)');

errmodel = zeros(1,1);

% Model 1: this is a naive estimate of the power
fprintf('\n\nModel_1 = current * voltage\n');
plot(y, y-p, '-g');
errmodel(1) = sqrt(sum((p - y).^2) / (2*m));
fprintf('\nerror in Model_1: %f W\n', errmodel(1));

%  Model 2 uses a second-order polynomial w.r.t. model1. i.e.:
%   estimate = theta1 * model1^0 + theta2 * model1^1 + theta3 * model1^2
fprintf('\n\nModel_2 = theta_1 + theta_2*Model_1 + theta_3*(Model_1)^2\n');
X = [ones(m, 1) p p.^2];
theta = normalEqn(X, y)
h = X * theta;
plot(y, y-h, '-w');
errmodel(2) = sqrt(sum((h - y).^2) / (2*m));
fprintf('\nerror in Model_2: %f W\n', errmodel(2));


%  Model 3 uses a second-order polynomial w.r.t. all available features:
%   current, voltage, and current * voltage
fprintf('\n\nModel_3 = 2nd order polynomial of all features:\n');
fprintf('\n\n  ones, c, c^2, v, v^2, c*v, v*c^2, c*v^2, (c*v)^2\n');
X = [ones(m, 1) c c.^2 v v.^2 p v.*c.^2 c.*v.^2 p.^2];
theta = normalEqn(X, y)
h = X * theta;
plot(y, y-h, '-r');
errmodel(3) = sqrt(sum((h - y).^2) / (2*m));
fprintf('\nerror in Model_3: %f W\n', errmodel(3));


%  Model 4 uses a second-order polynomial w.r.t. current, and first order:
%   w.r.t. voltage and power. Perhaps model 3 was overfitting?
fprintf('\n\nModel_4 = 2nd order polynomial of current, plus voltage and power:\n');
fprintf('\n\n  ones, c, c^2, v, p\n');
X = [ones(m, 1) c c.^2 v c.*v];
theta = normalEqn(X, y)
h = X * theta;
plot(y, y-h, '-c');
errmodel(4) = sqrt(sum((h - y).^2) / (2*m));
fprintf('\nerror in Model_4: %f W\n', errmodel(4));


%  Model 5 uses a second-order polynomial w.r.t. current, plus power
fprintf('\n\nModel_5 = 2nd order polynomial of current, plus power:\n');
fprintf('\n\n  ones, c^2, p\n');
X = [ones(m, 1) c.^2 p];
theta = normalEqn(X, y)
h = X * theta;
plot(y, y-h, '-m');
errmodel(5) = sqrt(sum((h - y).^2) / (2*m));
fprintf('\nerror in Model_5: %f W\n', errmodel(5));


legend('No Error', 'Model 1', 'Model 2', 'Model 3', 'Model 4', 'Model 5')


errmodel

hold off;
