const archiver = require('archiver');

/**
 * Empaqueta una carpeta completa en un zip, escribiendolo directo al
 * response stream (sin archivo temporal intermedio).
 */
function pipeDirAsZip(dirPath, res, downloadName) {
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', `attachment; filename="${downloadName}"`);

  const archive = archiver('zip', { zlib: { level: 9 } });
  archive.on('error', (err) => {
    res.status(500).end(String(err));
  });
  archive.pipe(res);
  archive.directory(dirPath, false);
  archive.finalize();
}

module.exports = { pipeDirAsZip };
