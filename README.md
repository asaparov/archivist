
`make_docs.py` is a script that converts XML output from [Doxygen](http://www.stack.nl/~dimitri/doxygen/) into static HTML webpages. As an example, the C++ documentation webpages for [my projects](https://asaparov.org/docs/core/) were generated using this script. I modeled the theme after [Google's Protocol Buffer API reference](https://developers.google.com/protocol-buffers/docs/reference/cpp/).

For convenience, I also added a `gulpfile.js` to streamline the process and further compile/compress the output HTML.

### Usage

1. Make sure you have [Doxygen](http://www.stack.nl/~dimitri/doxygen/) and Python 3 installed.
2. Place your library/repository folders into a single folder (the default directory is "..", i.e. the parent directory).
3. Edit the `Doxygen` configuration file as appropriate for your project (specifically, list the paths to each of your libraries/repositories in the INPUT option, and make sure GENERATE_HTML is disabled).
4. Edit the configuration variables at the top of `make_docs.py` as appropriate for your project. Make sure to change `src_root` to the folder containing your libraries/repositories.
5. Modify the `header.html`, `footer.html`, CSS, and Javascript files to your liking.

**If npm is installed:**

6. Simply run `npm install` and then `gulp`.

**If npm is not installed:**

6. Run `doxygen Doxyfile` to generate the XML in `Docs/xml/`.
7. Run `make_docs.py` to generate the HTML in `Docs/html/`.
