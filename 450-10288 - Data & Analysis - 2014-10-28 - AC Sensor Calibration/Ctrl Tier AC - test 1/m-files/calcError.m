function [rmsErr, errors] = calcError(h, y)

errors = h-y;
m = length(y);
rmsErr = sqrt(sum(errors.^2) / (2*m));
errors = errors'

end
