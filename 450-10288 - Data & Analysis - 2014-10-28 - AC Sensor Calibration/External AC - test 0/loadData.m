function [c, v, p, y] = loadData()

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

end
