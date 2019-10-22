import os, sys;
import numpy as np, pandas as pd;
from scipy.optimize import curve_fit;
from scipy.stats import lognorm;
import fitModels;

def equation(x,e,b): return (x**e)+b;
def ln_cdf_ne(x,u,s): return lognorm.cdf( x,s,scale=u );

m = fitModels.model();
m.equation = ln_cdf_ne;

data = pd.DataFrame({
    'x': [1,2,3,4,5,6],
});
data['y'] = m.predict(data['x'],2,4);
params = pd.Series({
    'u': np.nan,
    's': np.nan,
});
results, r2 = m.fit(data['x'], data['y'], params);
print(results);
print(r2);
data['predicted'] = m.predict(data['x'],*results);
print(data);






sys.exit();


params = pd.Series({
    'm': np.nan,
    'b': np.nan,
    'o': 0,
});
print(m.equation);
results, r2 = m.fit(data['x'], data['y'], params);
print(results);
