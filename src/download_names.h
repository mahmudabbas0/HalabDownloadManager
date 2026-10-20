#pragma once
namespace DownloadNames {
inline QString clean(QString name) {
    name.replace('\\','/'); name=name.section('/',-1).normalized(QString::NormalizationForm_C);
    name.replace(QRegularExpression("[<>:\\x22/\\\\|?*\\x00-\\x1f\\x7f\\x202a-\\x202e\\x2066-\\x2069]"),"_");
    name=name.trimmed();while(name.endsWith('.')||name.endsWith(' '))name.chop(1);
    if(name.isEmpty()||name=="."||name=="..")name="download";
    QString stem=QFileInfo(name).completeBaseName();
    if(QRegularExpression("^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$",QRegularExpression::CaseInsensitiveOption).match(stem).hasMatch())name="_"+name;
    if(name.size()>170){QString suffix=QFileInfo(name).suffix().left(20);name=name.left(145)+(suffix.isEmpty()?"":"."+suffix);}
    return name;
}
inline QString dispositionName(const QByteArray &header) {
    QString value=QString::fromLatin1(header);
    auto star=QRegularExpression(R"rx((?:^|;)\s*filename\*\s*=\s*(?:"([^"]*)"|([^;]*)))rx",QRegularExpression::CaseInsensitiveOption).match(value);
    if(star.hasMatch()){
        QString encoded=(star.captured(1).isEmpty()?star.captured(2):star.captured(1)).trimmed();int first=encoded.indexOf('\''),second=encoded.indexOf('\'',first+1);
        if(first>0&&second>first){auto bytes=QByteArray::fromPercentEncoding(encoded.mid(second+1).toLatin1());QString charset=encoded.left(first).toLower();if(charset=="utf-8")return clean(QString::fromUtf8(bytes));if(charset=="iso-8859-1")return clean(QString::fromLatin1(bytes));}
    }
    auto plain=QRegularExpression(R"rx((?:^|;)\s*filename\s*=\s*(?:"((?:\\.|[^"])*)"|([^;]*)))rx",QRegularExpression::CaseInsensitiveOption).match(value);
    if(!plain.hasMatch())return {};
    QString name=plain.captured(1).isEmpty()?plain.captured(2).trimmed():plain.captured(1);
    name.replace("\\\"","\"");return name.isEmpty()?QString():clean(name);
}
inline QString extensionForMime(QString type){type=type.section(';',0,0).trimmed().toLower();static const QMap<QString,QString> known{{"audio/mpeg","mp3"},{"audio/mp3","mp3"},{"application/zip","zip"},{"application/x-zip-compressed","zip"},{"video/mp4","mp4"},{"application/pdf","pdf"},{"audio/wav","wav"},{"audio/x-wav","wav"},{"application/x-rar-compressed","rar"},{"application/vnd.rar","rar"},{"application/x-7z-compressed","7z"}};if(known.contains(type))return known[type];if(type=="application/octet-stream"||type.isEmpty())return {};return QMimeDatabase().mimeTypeForName(type).preferredSuffix();}
inline QString propose(QNetworkReply*r,QString original,bool automatic){
    QString name=clean(QFileInfo(original).fileName()),mime=QString::fromLatin1(r->rawHeader("Content-Type"));
    if(automatic){auto server=dispositionName(r->rawHeader("Content-Disposition"));auto redirected=clean(QFileInfo(r->url().path()).fileName());if(!server.isEmpty())name=server;else if(!QFileInfo(redirected).suffix().isEmpty()&&!QStringList{"php","asp","aspx","jsp","cgi"}.contains(QFileInfo(redirected).suffix().toLower()))name=redirected;}
    QString suffix=QFileInfo(name).suffix().toLower();if(suffix.isEmpty()||QStringList{"php","asp","aspx","jsp","cgi","bin"}.contains(suffix)){QString ext=extensionForMime(mime);if(!ext.isEmpty()){if(!suffix.isEmpty())name=QFileInfo(name).completeBaseName();name+="."+ext;}}
    return clean(name);
}
inline QString unique(QString folder,QString name,const std::function<bool(QString)>&taken){name=clean(name);QString path=QDir(folder).filePath(name);int n=1;while(taken(path)){QString ext=QFileInfo(name).suffix();path=QDir(folder).filePath(QFileInfo(name).completeBaseName()+" ("+QString::number(n++)+")"+(ext.isEmpty()?"":"."+ext));}return path;}
inline bool signatureOkay(QString path,const QByteArray &data){auto ext=QFileInfo(path).suffix().toLower();if(ext=="zip")return data.startsWith("PK\x03\x04")||data.startsWith("PK\x05\x06")||data.startsWith("PK\x07\x08");if(ext=="mp3")return data.startsWith("ID3")||(data.size()>1&&uchar(data[0])==0xff&&(uchar(data[1])&0xe0)==0xe0);if(ext=="pdf")return data.left(1024).contains("%PDF-");if(ext=="7z")return data.startsWith(QByteArray::fromHex("377abcaf271c"));if(ext=="rar")return data.startsWith("Rar!");return true;}
}

inline QIcon categoryIcon(QString category,int size=24){
    QPixmap image(size*2,size*2);image.fill(Qt::transparent);QPainter p(&image);p.setRenderHint(QPainter::Antialiasing);p.scale(size*2/24.,size*2/24.);p.setPen(QPen(QColor("#d6e3ef"),1.5,Qt::SolidLine,Qt::RoundCap,Qt::RoundJoin));
    if(category=="Video"){p.setBrush(QColor("#6c9fdd"));p.drawRoundedRect(QRectF(2,4,20,16),3,3);p.setPen(Qt::NoPen);p.setBrush(Qt::white);p.drawPolygon(QPolygonF{QPointF(10,8),QPointF(16,12),QPointF(10,16)});}
    else if(category=="Music"){p.setPen(QPen(QColor("#c7a2ee"),2));p.drawLine(10,5,20,3);p.drawLine(10,5,10,17);p.drawLine(20,3,20,15);p.setBrush(QColor("#c7a2ee"));p.drawEllipse(QRectF(4,16,6,4));p.drawEllipse(QRectF(14,14,6,4));}
    else if(category=="Compressed"){p.setPen(Qt::NoPen);for(int i=0;i<3;++i){p.setBrush(QColor(i==0?"#a37bd8":i==1?"#6db78a":"#d89c64"));p.drawRoundedRect(QRectF(3,3+i*6,18,5),1,1);}p.setBrush(QColor("#e5c67d"));p.drawRect(QRectF(11,2,3,19));}
    else if(category=="Programs"){p.setBrush(QColor("#599cbb"));p.drawRoundedRect(QRectF(2,3,20,15),2,2);p.drawLine(8,22,16,22);p.drawLine(12,18,12,22);p.setPen(QPen(Qt::white,1.5));p.drawLine(6,8,9,10);p.drawLine(9,10,6,12);p.drawLine(12,12,17,12);}
    else if(category=="Documents"){p.setBrush(QColor("#c5d8e6"));p.drawRoundedRect(QRectF(5,2,14,20),2,2);p.setPen(QPen(QColor("#56758c"),1.5));for(int y:{8,12,16})p.drawLine(8,y,16,y);}
    else{p.setBrush(QColor(category=="Finished"?"#84b798":"#d3b96d"));p.drawRoundedRect(QRectF(2,6,20,15),2,2);p.drawRoundedRect(QRectF(2,3,9,6),1,1);if(category=="Finished"){p.setPen(QPen(QColor("#244e39"),2));p.drawLine(7,13,10,16);p.drawLine(10,16,17,10);}}
    image.setDevicePixelRatio(2);return QIcon(image);
}
