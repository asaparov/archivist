var paths = {};

// Directory locations.
paths.assetsDir       = '';						// The files Gulp will handle.
paths.siteDir         = 'Docs/compiled_html/';	// The resulting static site.
paths.siteAssetsDir   = 'Docs/compiled_html/';	// The resulting static site's assets.

// Folder naming conventions.
paths.fontFolderName      = 'fonts';
paths.srcImageFolderName  = 'Docs/html';
paths.imageFolderName     = '';
paths.srcAssetFolderName  = 'Docs/html';
paths.assetFolderName     = '';
paths.srcScriptFolderName = 'Docs/html';
paths.scriptFolderName    = 'js';
paths.srcStylesFolderName = 'Docs/html';
paths.stylesFolderName    = 'css';
paths.srcHtmlFolderName   = 'Docs/html';

// Asset files locations.
paths.cssFiles    = paths.assetsDir + paths.srcStylesFolderName;
paths.jsFiles     = paths.assetsDir + paths.srcScriptFolderName;
paths.imageFiles  = paths.assetsDir + paths.srcImageFolderName;
paths.assetFiles  = paths.assetsDir + paths.srcAssetFolderName;
paths.fontFiles   = paths.assetsDir + paths.fontFolderName;

// Site files locations.
paths.siteCssFiles   = paths.siteAssetsDir + paths.stylesFolderName;
paths.siteJsFiles    = paths.siteAssetsDir + paths.scriptFolderName;
paths.siteImageFiles = paths.siteAssetsDir + paths.imageFolderName;
paths.siteAssetFiles = paths.siteAssetsDir + paths.assetFolderName;
paths.siteFontFiles  = paths.siteAssetsDir + paths.fontFolderName;

// Glob patterns by file type.
paths.cssPattern      = '/**/*.css';
paths.jsPattern       = '/**/*.js';
paths.assetPattern    = '/**/*.+(pdf|py)';
paths.imagePattern    = '/**/*.+(jpg|JPG|jpeg|JPEG|png|PNG|svg|SVG|gif|GIF|webp|WEBP|tif|TIF)';
paths.markdownPattern = '/**/*.+(md|MD|markdown|MARKDOWN)';
paths.htmlPattern     = '/**/*.html';
paths.xmlPattern      = '/**/*.xml';

// Asset files globs
paths.cssFilesGlob   = paths.cssFiles  + paths.cssPattern;
paths.jsFilesGlob    = paths.jsFiles    + paths.jsPattern;
paths.imageFilesGlob = paths.imageFiles + paths.imagePattern;
paths.assetFilesGlob = paths.assetFiles + paths.assetPattern;

// Site files globs
paths.siteHtmlFilesGlob = paths.siteDir + paths.htmlPattern;

module.exports = paths; 
