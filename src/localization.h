#pragma once
namespace L {
inline QString language="ar";
inline QJsonObject catalogs;
inline QTranslator qtCatalog;
inline QString text(const QString &source){if(catalogs.isEmpty()){QFile f(":/i18n/languages.json");if(f.open(QIODevice::ReadOnly))catalogs=QJsonDocument::fromJson(f.readAll()).object();}return catalogs.value(language).toObject().value(source).toString(source);}
inline QString stored(QObject*o,const char*key,QString raw){QByteArray sourceKey=QByteArray("_src_")+key,lastKey=QByteArray("_last_")+key;auto source=o->property(sourceKey);if(!source.isValid()||raw!=o->property(lastKey).toString()){source=raw;o->setProperty(sourceKey,raw);}QString translated=text(source.toString());o->setProperty(lastKey,translated);return translated;}
inline void apply(QObject *root){
 QList<QObject*> objects{root};objects.append(root->findChildren<QObject*>());
 for(auto o:objects){
  if(auto a=qobject_cast<QAction*>(o)){a->setText(stored(o,"text",a->text()));a->setToolTip(text(o->property("_src_text").toString()).remove('&'));}
  if(auto w=qobject_cast<QWidget*>(o)){if(w->isWindow()||qobject_cast<QDockWidget*>(w))w->setWindowTitle(stored(o,"title",w->windowTitle()));}
  if(auto b=qobject_cast<QAbstractButton*>(o))if(!qobject_cast<QToolButton*>(b))b->setText(stored(o,"text",b->text()));
  if(auto label=qobject_cast<QLabel*>(o))label->setText(stored(o,"text",label->text()));
  if(auto edit=qobject_cast<QLineEdit*>(o))edit->setPlaceholderText(stored(o,"placeholder",edit->placeholderText()));
  if(auto combo=qobject_cast<QComboBox*>(o)){for(int i=0;i<combo->count();++i){QString source=combo->itemData(i,Qt::UserRole+33).toString();if(source.isEmpty()){source=combo->itemText(i);combo->setItemData(i,source,Qt::UserRole+33);}combo->setItemText(i,text(source));}}
  if(auto tabs=qobject_cast<QTabWidget*>(o)){for(int i=0;i<tabs->count();++i){auto key=QByteArray("_tab_")+QByteArray::number(i);QString source=tabs->property(key).toString();if(source.isEmpty()){source=tabs->tabText(i);tabs->setProperty(key,source);}tabs->setTabText(i,text(source));}}
  if(auto tree=qobject_cast<QTreeWidget*>(o)){QTreeWidgetItemIterator it(tree);while(*it){auto item=*it;QString source=item->data(0,Qt::UserRole+33).toString();if(source.isEmpty()){source=item->text(0);item->setData(0,Qt::UserRole+33,source);}item->setText(0,text(source));++it;}}
  if(auto table=qobject_cast<QTableWidget*>(o)){for(int i=0;i<table->columnCount();++i)if(auto item=table->horizontalHeaderItem(i)){QString source=item->data(Qt::UserRole+33).toString();if(source.isEmpty()){source=item->text();item->setData(Qt::UserRole+33,source);}item->setText(text(source));}}
 }
 for(auto bar:root->findChildren<QToolBar*>())for(auto action:bar->actions())if(auto button=qobject_cast<QToolButton*>(bar->widgetForAction(action))){button->setFont(QFont("Segoe UI",9));button->setFixedWidth(qMax(98,button->fontMetrics().horizontalAdvance(action->text())+44));button->setFixedHeight(80);}
}
inline void setLanguage(QString value){language=QStringList{"ar","en","tr"}.contains(value)?value:"en";qApp->removeTranslator(&qtCatalog);if(language!="en"&&qtCatalog.load("qtbase_"+language,QCoreApplication::applicationDirPath()+"/translations"))qApp->installTranslator(&qtCatalog);qApp->setLayoutDirection(language=="ar"?Qt::RightToLeft:Qt::LeftToRight);}
class DialogFilter:public QObject{
 bool eventFilter(QObject*o,QEvent*e)override{if(e->type()==QEvent::Show&&qobject_cast<QDialog*>(o)){apply(o);if(auto w=qobject_cast<QWidget*>(o)){w->setLayoutDirection(language=="ar"?Qt::RightToLeft:Qt::LeftToRight);if(auto form=w->findChild<QFormLayout*>())form->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);}}return false;}
};
}
