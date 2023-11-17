function [err] = calcError(h, y)

m = length(y);
err = sqrt(sum((h - y).^2) / (2*m));

end
