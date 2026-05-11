exports.ok = (res, data, message='OK') => res.json({ success:true, message, data });
exports.fail = (res, status=500, message='Erro interno', error=null) => res.status(status).json({ success:false, message, error: process.env.NODE_ENV === 'production' ? undefined : error?.message || error });
