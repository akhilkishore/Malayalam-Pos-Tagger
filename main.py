from flask import Flask, jsonify,request,render_template,make_response
from flask import *
import json 
import pickle
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "spc"
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'akhil.mi3@iiitmk.ac.in',
	MAIL_PASSWORD = 'Highasme.13896'
	)
mail = Mail(app)





def untag(tagged_sentence):
    return [w for w, t in tagged_sentence]
 
def features(sentence, index):
    """ sentence: [w1, w2, ...], index: the index of the word """
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'is_numeric': sentence[index].isdigit()
        #'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }

def readmsg( mail):
    msg = Message(mail, sender=mail, recipients=["akhilkishorek13@gmail.com"])
    return msg

	
def pos_tag(sentence, loaded_model):
    tags = loaded_model.predict([features(sentence, index) for index in range(len(sentence))])
    return tags
 
 #[('This', u'DT'), ('is', u'VBZ'), ('my', u'JJ'), ('friend', u'NN'), (',', u','), ('John', u'NNP'), ('.', u'.')]
def transform_to_dataset(tagged_sentences):
        X, y = [], []
    

        for tagged in tagged_sentences:
            for index in range(len(tagged)):
                X.append(features(untag(tagged), index))
                y.append(tagged[index][1])
    
        return X, y

def readData():
    f = open("Malayalam_Tagged_Data.txt","r")
    data = f.read()
    data = data.split(".        \RD_PUNC")
    all_sent = []
    for x in data:
        x = x.split("\n")
        v = []
        for y in x:
            if y != "":
                y = y.replace("\\","")
                y = y.split("        ")
                v.append( (y[0],y[1]) )
        v.append(('.','RD_PUNC'))
        all_sent.append(v)
    del data
    tagged_sentences = all_sent
    #Split the dataset for training and testing
    cutoff = int(.75 * len(tagged_sentences))
    training_sentences = tagged_sentences[:cutoff]
    test_sentences = tagged_sentences[cutoff:]
    

    filename = 'finalized_model2.sav'

    loaded_model = pickle.load(open(filename, 'rb'))
    
   
    
    X, y = transform_to_dataset(training_sentences)
    return X, y, loaded_model
  #  print(pos_tag("ഇന്ത്യന്‍ റെയില്‍വേ കാറ്ററിങ് ആന്‍ഡ് ടൂറിസം കോര്‍പ്പറേഷന്റെ മുംബൈ ബോട്ടിലിങ് പ്ലാന്റിലാണ് ഈ കുപ്പിവെള്ളം ഉല്‍പ്പാദിപ്പിക്കുക .".split(" "),loaded_model) )
#

X, y, loaded_model = readData()





##############################################################################################################################

##############################################################################################################################
@app.route('/')
def index():
    readData()
    return render_template('index.html') #if no : calling index page

@app.route('/generateTags', methods=['POST'])
def login():
    print("called")
    response = request.data
    #response = response.decode('ascii')
    print(response)
    print(type(response))
    response = json.loads(response)
    print(response)
    text = response['data'].replace("/",'')
    text = response['data'].replace("-",'')
    text = response['data'].replace("&",'')
    text = response['data'].replace("*",'')


    sentence =  text.split(" ")
    while("" in sentence) : 
        sentence.remove("") 
    print(sentence)
    posTags = pos_tag(sentence, loaded_model)
    result = ""
    for x in range(0,len(posTags)): 
        if sentence[x] in ['.',',','?','!']:
            result += sentence[x]
            result += " - "
            result += 'RD_PUNC'#posTags[x]
            result += "   "
        else:
            result += sentence[x]
            result += " - "
            result += posTags[x]
            result += "   "
    print(result)
    return jsonify(result)

@app.route('/send-mail/', methods=['post'])
def send_mail():
        q = request.data
        q = q.decode('ascii')
        q = json.loads(q)
        print(q)
        msg = readmsg(q['email'])
        msg.body = q['email']+" is tried to connect you."    
        mail.send(msg)       
        return 'Mail sent!'


##############################################################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500,debug=True) #port  4500 