import numpy as np, pandas as pd;
from scipy.optimize import curve_fit;
from scipy.optimize import leastsq;
from scipy.stats import lognorm;
class model(object):
    def __init__(s):
        s.eval_safe = {
        };
        def default_equation(x,m,b,o):
            return m*x+b+o;
        s.equation = default_equation;
        s.params = None;

    def predict(s,x,*params):
        return [ s.equation(xv,*params) for xv in x ];

    def fit(s,x,y,params,curve_fit_kwargs={}):
        # uses eval and lambda function to handle fixed/free parameters
        # all parameters in params that are np.nan are free (will be fit)
        # all that are not np.nan are fixed and value will be passed to equation
        # ----------------------------------------------------------------------
        # build lambda with non-fixed parameters as arguments for curve_fit
        code = "lambda x, "+", ".join(params[params.isnull()].index)+": ";
        # build equation call that includes all parameter arguments
        code += "equation(";
        code += "x, "+", ".join(params.index)+")";
        # build locals available for eval
        locals = {'equation': s.equation};
        locals = dict( **locals, **s.eval_safe );
        # add fixed parameters to locals as variables named by parameter index
        for p,v in params[params.notnull()].iteritems():
            locals[p] = v;
        # get eval'd lambda
        # TODO: need to restrict this to make it more secure later
        e = eval(code, locals);
        # run curve_fit using the lambda
        popt, pcov = curve_fit(e, x, y, **curve_fit_kwargs);
        # store fit parameter results (order is essential here)
        presults = params.copy();
        presults[presults.isnull()] = popt;
        # calculate r2
        exp_y = s.predict(x,*presults);
        perr = np.sqrt(np.diag(pcov));
        _res = np.subtract(y,exp_y);
        _ssres = np.sum(_res**2);
        _sstot = np.sum( np.subtract( y,y.mean() )**2 );
        r2 = 1-(_ssres/_sstot);
        return presults, r2;

# ################################################################################
# # LOGNORMAL CDF FIT
# ################################################################################
# def ln_cdf_ne(x,u,s): return lognorm.cdf( x,s,scale=u );
# def ln_pdf_ne(x,u,s): return lognorm.pdf( x,s,scale=u );
# # exponential for graphing
# def ln_cdf(x,u,s): return lognorm.cdf( x,s,scale=np.expm1(u) );
# def ln_pdf(x,u,s): return lognorm.pdf( x,s,scale=np.expm1(u) );
# def ln_ppf(x,u,s): return lognorm.ppf( x,s,scale=np.expm1(u) );
#
# def fit_lognormal(x,y,**kwargs):
#     r = pd.Series(index=[
#         'ln_u',
#         'ln_s',
#         'ln_r2',
#         'ln_n',
#     ]);
#     if len(y) != len(x):
#         raise Exception("x and y must have the same shape");
#     if len(y) <= 2:
#         raise Exception("need at least 3 points for a fit");
#     try:
#         popt, pcov = curve_fit(
#             ln_cdf_ne,
#             x,
#             y,
#             **kwargs
#         );
#         perr = np.sqrt(np.diag(pcov));
#         _res = np.subtract(y,ln_cdf_ne(x,*popt));
#         _ssres = np.sum( _res**2 );
#         _sstot = np.sum( np.subtract( y,y.mean() )**2 );
#         r['ln_u'] = np.log1p(popt[0]);
#         r['ln_s'] = popt[1];
#         r['ln_r2'] = 1 - (_ssres/_sstot);
#         r['ln_n'] = len(y);
#     except:
#         raise;
#     return r;
# def fitted_lognormal(x,r):
#     df = pd.DataFrame(columns=['x','y']);
#     df['x'] = x;
#     df['y'] = ln_cdf_ne(df['x'], np.exp(r['ln_u']), r['ln_s']);
#     return df.copy();
# def lognormal_metrics(fit,p=np.exp(-1/2)):
#     # starting points
#     u = fit['ln_u'];
#     s = fit['ln_s'];
#     # probability height for PDF for left/right/duration
#     z = np.sqrt(2 * np.log(1/p));	# default is ~60.65%
#     dmax_left = np.divide(
#         1,
#         np.multiply( s, np.sqrt( 2*np.pi ) )
#     );
#     dmax_right = np.exp( np.subtract(
#         np.divide( s**2, 2 ),
#         u
#     ) );
#     delay = np.exp(np.subtract(u,(s**2)));
#     left = delay * np.exp( -s*z );
#     right = delay * np.exp( s*z );
#     duration = right - left;
#     r = pd.Series({
#         'delay'			: delay,
#         'log2_delay'	: np.log(delay) / np.log(2),
#         'dmax'			: np.multiply(dmax_left, dmax_right),
#         'left'			: left,
#         'log2_left'		: np.log(left)/np.log(2),
#         'right'			: right,
#         'log2_right'	: np.log(right)/np.log(2),
#         'duration'		: duration,
#     });
#     if len(r)==1: return r.iloc[0];
#     return r;
# ################################################################################
