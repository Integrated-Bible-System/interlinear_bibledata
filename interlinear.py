import _mysql
import json
db=_mysql.connect("localhost","root","couchbase","default")
stat_file = open("stats.json")
stats = json.load(stat_file)
book_file = open("books.json")
books = json.load(book_file)

def dump_book(name, bno):

  interlinear = []

  # get num chapters
  nchapters = int(len(stats[bno].keys()))
  print (name, nchapters)

  # iterate over each chapter of the book
  for i in xrange(1,nchapters+1):
   cno = str(i)
   nverses = int(stats[bno][cno])+1
   for j in xrange(1,nverses):
    vno = str(j)
    db.query("""select strongs from bible_original where book={} and chapter={} and verse={}""".format(bno, cno, vno))
    r=db.use_result()
   
    # load json chapter
    path="src/"+name+"/"
    filename = path+cno+".json"
    with open(filename) as data_file:

        # get the unordered json verse
        uverse = json.load(data_file)[vno]
        while True:
          val = r.fetch_row()
          if len(val) == 0:
             break

          # get strongs num
          strongs_prefix = 'h'
          if int(bno) >= 40:
              strongs_prefix = 'g'
          strongs = strongs_prefix+val[0][0]

          # lookup interlinear text
          match = [v for v in uverse if v['number'] == strongs]
          if len(match) > 0:
             interlinear.append(match[0])
          else:
             no_match = {"text": "", "number": strongs}
             interlinear.append(no_match)

  return interlinear

if __name__ == "__main__":

  # iterate over all the books
  for b in books:
  
    # get data
    name = b["n"] 
    bno=str(b["b"])
    data = dump_book(name, bno)
  
    # write out 
    book = open("interlinear/"+name+".json", "w")
    jsdata = json.dumps(data)
    book.write(jsdata)
