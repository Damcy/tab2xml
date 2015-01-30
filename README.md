# tab2xml

## overview
**tab2xml** convert tab format data to xml format data, according your confs.

### input-sample
format: damcy1 \t peking \t hello \t world

eg: damcy2`	`china`	`生活是简明、安静和值得尝试的

### output-sample
\<person>\<name><![CDATA[damcy1]]>\</name>\<location><![CDATA[peking]]>\</location>\<description><![CDATA[hello world]]>\</description>\</person>

\<person>\<name><![CDATA[damcy2]]>\</name>\<location><![CDATA[china]]>\</location>\<description><![CDATA[生活是简明、安静和值得尝试的]]>\</description>\</person>

## RUN
cat test.data | python ./scripts/table2xml.py --type=person --readConf=./conf/demo.tabFormat --xmlConf=./conf/demo.xml --tagConf=./conf/demo.tag

## args
####readlConf
your input tab format, it works when convert input raw data to dict format

see conf/demo.tabFormat
####xmlConf
output xml format

\<person>\<name><![CDATA[##name##]]>\</name>\<location><![CDATA[##where##]]>\</location>\<description><![CDATA[##info##]]>\</description>\</person>

just replace DATA pos with ##`element name`##

`element name` is defined in readConf


####tagConf
name match \<name>

where match \<location>

info match \<description>

so

{
    "name": "name",
    "info": "description",
    "where": "location"
}