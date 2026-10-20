#pragma once
#include <QProcess>
#ifdef Q_OS_WIN
#include <windows.h>
#endif
namespace HalabTools {
inline QString tool(QString name){QString root=QCoreApplication::applicationDirPath()+"/tools/";if(QFile::exists(root+name+".exe"))return root+name+".exe";return QStandardPaths::findExecutable(name);}
inline QString ffmpegDir(){QString path=QCoreApplication::applicationDirPath()+"/tools/ffmpeg/ffmpeg-N-127696-g8b3525e718-win64-lgpl-shared/bin";if(QFile::exists(path+"/ffmpeg.exe"))return path;auto found=QStandardPaths::findExecutable("ffmpeg");return found.isEmpty()?QString():QFileInfo(found).absolutePath();}
inline QStringList baseArgs(){QStringList args{"--ignore-config","--no-playlist","--no-warnings","--no-remote-components","--socket-timeout","20"};auto node=tool("node");if(!node.isEmpty())args<<"--js-runtimes"<<"node:"+node;auto ff=ffmpegDir();if(!ff.isEmpty())args<<"--ffmpeg-location"<<ff;return args;}
inline void hidden(QProcess &process){
#ifdef Q_OS_WIN
process.setCreateProcessArgumentsModifier([](QProcess::CreateProcessArguments*a){a->flags|=CREATE_NO_WINDOW;});
#endif
}
inline QString profile(){auto dir=qEnvironmentVariable("HALAB_DATA_DIR");if(dir.isEmpty())dir=QStandardPaths::writableLocation(QStandardPaths::AppLocalDataLocation);return QDir::cleanPath(dir);}
inline QString serverName(){return "HalabDM-"+QString::fromLatin1(QCryptographicHash::hash(profile().toUtf8(),QCryptographicHash::Sha256).toHex().left(24));}
inline bool validUrl(QString text){QUrl url(text);return url.isValid()&&!url.host().isEmpty()&&QStringList{"http","https"}.contains(url.scheme())&&text.size()<16384;}
}
