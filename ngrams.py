from WikiExtractor import process_dump, options, Extractor, logging, get_url
from io import StringIO
import db
from nlp import get_token_counts
import time
from multiprocessing import Process, Queue

from timeout import timeout

options.keepLinks = False
options.keepSections = False
options.keepLists = False
options.toHTML = False
options.write_json = True
options.print_revision = False
options.filter_disambig_pages = True

options.quiet = False
options.debug = False
options.log_file = "log.txt"

input_file="wiki.dump.bz2"
output_path="output"
file_size = 1000 * 1024

MAX_RETRIES=5

def extract_process(opts, i, jobs_queue, output_queue):
    """Pull tuples of raw page content, do CPU/regex-heavy fixup, push finished text
    :param i: process id.
    :param jobs_queue: where to get jobs.
    :param output_queue: where to queue extracted text for output.
    """

    out = StringIO()                 # memory buffer
    while True:
        logging.debug("Looking for extract job")
        job = jobs_queue.get()  # job is (id, title, page, page_num)
        logging.debug("got extract job")
        if job:
            id, revid, title, page, page_num = job
            try:
                e = CustomExtractor(*job[:4]) # (id, revid, title, page)
                page = None              # free memory
                e.extract(out)
                text = out.getvalue()
            except:
                text = ''
                logging.exception('Processing page: %s %s', id, title)

            output_queue.put((page_num, text))
            out.truncate(0)
            out.seek(0)
        else:
            logging.info('Quit extractor')
            break
    out.close()

def get_token_counts_process(queue, text):
    toks = get_token_counts(text)
    queue.put(toks)

class CustomExtractor(Extractor):
    def write_output(self, out, lines, retry=0):
        """
        :param out: a memory file
        :param text: the text of the page
        """
        if retry == MAX_RETRIES:
            raise Exception("Failed to add " + self.id + " " + self.title)

        start = time.time()
        logging.info("DOC %s %s %d", self.id, self.title, retry)
        text = '\n'.join(lines)

        queue = Queue()
        tok_proc = Process(target=get_token_counts_process, args=(queue, text))
        tok_proc.start()

        try:
            logging.info("get tc %s %s", self.id, self.title)
            with timeout(5):
                tok_proc.join()
                token_counts = queue.get()
            logging.info("got tc %s %s", self.id, self.title)
        except TimeoutError as e:
            logging.error("Timed out while waiting for token counts: %s %s", self.id, self.title)
            return self.write_output(out, lines, retry+1)

        try:
            logging.info("proc doc %s %s", self.id, self.title)
            db.process_document(self.id, self.title, token_counts)
            logging.info("done doc %s %s", self.id, self.title)
        except Exception as e:
            logging.error("Error while processing %s %s %d: %s", self.id, self.title, retry, e)
            return self.write_output(out, lines, retry+1)

        end = time.time()
        logging.info("TOOK %s %.2fs", self.id, end - start)

process_dump(input_file, None, output_path, file_size,
             False, 1, extract_process)

