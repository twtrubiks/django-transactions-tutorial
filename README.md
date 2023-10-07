# django-transactions-tutorial

django-transactions-tutorial 基本教學 - 了解 transactions 概念 📝

分支 [django_4_postgresql](https://github.com/twtrubiks/django-transactions-tutorial/tree/django_4_postgresql) 有 django 4 以及 pg 的版本.

* [Youtube Tutorial PART 1 - Django 如何連結 MySQL](https://youtu.be/0IKuKk8ubf0)
* [Youtube Tutorial PART 2 - Transaction 概念簡介](https://youtu.be/P67IfMK4Y5g)
* [Youtube Tutorial PART 3 - Django 實戰 Transaction - Atomicity](https://youtu.be/aG33kaSmgzI)
* [Youtube Tutorial PART 4 - Django 實戰 Transaction - Consistency and Isolation](https://youtu.be/m7JIHU9mLW4)

建議在閱讀這篇的時候，對 Djagno 已經有稍微基礎的認識，可參考我之前寫的

* [Django 基本教學 - 從無到有 Django-Beginners-Guide](https://github.com/twtrubiks/django-tutorial)
* [Django-REST-framework 基本教學 - 從無到有 DRF-Beginners-Guide 📝](https://github.com/twtrubiks/django-rest-framework-tutorial)

## 教學

由於這邊我會使用 MySQL＋Django 當做範例，所以我會先帶大家設定 MySQL 和 Django:relaxed:

### Django 如何連結 MySQL

* [Youtube Tutorial PART 1 - Django 如何連結 MySQL](https://youtu.be/0IKuKk8ubf0)

請安裝 [PyMySQL](https://github.com/PyMySQL/PyMySQL) 這個 Library，請執行以下指令

```cmd
pip install PyMySQL
```

以及 [mysqlclient](https://github.com/PyMySQL/mysqlclient-python) 這個 Library，請執行以下指令

```cmd
pip install mysqlclient
```

或是也可以直接安裝 [requirements.txt](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/requirements.txt)

```cmd
pip install -r requirements.txt
```

這邊直接使用 Docker 來安裝 MySQL，如果你不了解什麼是 Docker，可參考我之前的教學

* [Docker 基本教學 - 從無到有 Docker-Beginners-Guide 📝](https://github.com/twtrubiks/docker-tutorial)

安裝  MySQL

```cmd
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password123 -d mysql
```

![alt tag](https://i.imgur.com/P9R6zp5.png)

接著直接用 tool 連接 MySQL 即可，可以用 [workbench](https://www.mysql.com/products/workbench/)，

如下圖輸入連接資訊

![alt tag](https://i.imgur.com/Z08pJPP.png)

可以按 Test Connection 確認是否連接成功

![alt tag](https://i.imgur.com/lLCrr3P.png)

成功進去後，建立一顆名稱為 demo 的 database

![alt tag](https://i.imgur.com/cSzddhN.png)

範例可參考 [settings.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/django_transaction/settings.py)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'demo',
        'USER': 'root',
        'PASSWORD': 'password123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}
```

基本上這樣就設定完成了。

[model.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py) 如下

```python
class Item(models.Model):
    stock = models.IntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    """ track of changes """
    version = models.IntegerField(default=0)
```

接著執行 database migrate

```python
python manage.py makemigrations
```

```python
python manage.py migrate
```

可用 [workbench](https://www.mysql.com/products/workbench/) 查看 database

![alt tag](https://i.imgur.com/9d181Dk.png)

讓我們透過 Python Console 來新增一筆資料，

```python
from items.models import Item
Item.objects.create(stock=100,price=10)
```

![alt tag](https://i.imgur.com/d7ZHGwy.png)

查看 database

![alt tag](https://i.imgur.com/yxiMWWg.png)

## Transaction

* [Youtube Tutorial PART 2 - Transaction 概念簡介](https://youtu.be/P67IfMK4Y5g)

Transaction Isolation 有四大特性，又稱 ACID，下面將一一介紹:smirk:

### Atomicity

又稱原子性，交易就像是原子一樣，不可分割，假設今天有 10 筆連續的交易，那結果只會有兩種，第一種，

全部成功，第二種，全部失敗。如果有任何一筆資料失敗，db 則會 rollback ( rollback 就是回到交易前的狀態 )，

也就是好像什麼事情都沒發生過一樣，不允許是幾筆成功，幾筆失敗類似這樣的狀況。

### Consistency

又稱一致性，交易前以及交易後的資料庫完整性，可能有點抽象，沒關係，我舉個例子，假設 A 戶頭有 200 元，

B 戶頭有 600 元，兩個戶頭加起來是 800 元，今天 A 要匯款 100 元給 B，結果應該是 A 戶頭變 100 元，B 戶頭變

700 元，兩個戶頭加起來還是 800 元，這就是 Consistency，不可以發生 A 戶頭被扣款了 100 元，但是 B 戶頭卻沒

有被加上 100 元的狀況 ( 也就是 A 戶頭變 100 元，B 戶頭卻還是 600 元 ，兩個戶頭加起卻變成了 700 元 ) ，因為

這樣會破壞資料的一致性 ，交易前後的資料必須完整一致。

### Isolation

又稱隔離性，資料庫允許多個並發交易，也就是同時對資料進行讀寫以及修改的能力，隔離性主要是為了防止多個

並發交易（ 同時對一個資料進行讀寫 ），導致資料不一致的情況。我知道可能還是有點黑人問號 :question::question::question::question:

所以我這邊也舉個例子，假設一個購物網站，是用儲值的方式消費，目前 A 的餘額是 500 元，於是 A 打開了兩個

視窗分別購買 400 元的衣服以及 200 元的杯子，如果我們沒有將 A 的餘額鎖定起來，這樣可能會導致，第一個視窗

500 元扣掉 400 元（ 購買成功 ），第二個視窗卻還是 500 元扣掉 200 元（ 購買成功），這樣的狀況是不被允許的，

理論上，A 的餘額只能購買其中一項東西而已，也就是 A 的餘額應該被鎖定起來，第一個視窗做完之後，第二個視窗

的動作才能繼續進行。

Isolation levels 有四種，分別為 Serializable ( 可序列化 )、Repeatable reads ( 可重複讀 )、Read committed ( 提交讀 )

、Read uncommitted ( 未提交讀 )。詳細的介紹這邊就不提了，可參考 [Transaction Isolation - wiki](https://zh.wikipedia.org/wiki/%E4%BA%8B%E5%8B%99%E9%9A%94%E9%9B%A2)。

### Durability

又稱持久性，當交易結束後，對資料的修改就是永久的，即使系統故障，資料也不會遺失。

## Django 實戰 Transaction

前面介紹了那麼多，一定要來實戰一下 :satisfied:

* [Youtube Tutorial PART 3 - Django 實戰 Transaction - Atomicity](https://youtu.be/aG33kaSmgzI)

首先，以下是 [models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)，由於很簡單，我就不詳細介紹:relieved:

```python
class Item(models.Model):
    stock = models.IntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    """ track of changes """
    version = models.IntegerField(default=0)
```

讓我們來看看 Atomicity 的例子，簡單說明一下，這邊我會模擬新增 5 筆資料，其中一筆資料異常，

依照 ACID 的原則，應該全部的資料都不能進資料庫，也就是好像什麼事情都沒發生過一樣。

沒有 transaction 的情況，

[models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)

```python
def create_items_no_transaction(**kwargs):
    count = int(kwargs.get('count'))
    result_code = 200
    try:
        for i in range(0, count):
            if i == count - 2:
                Item.objects.create(stock=100, price='error')
            else:
                Item.objects.create(stock=100, price=10)
    except Exception as e:
        Exception('Unexpected error: {}'.format(e))
        result_code = 500
    return result_code
```

簡單解釋一下 code ，在倒數第二筆的資料將他填入一個錯誤的資料（ price 填入字串 ），觀察結果。

這邊直接使用 [postman](https://www.getpostman.com/) 測試。

![alt tag](https://i.imgur.com/WWwCRLm.png)

如下圖，你會發現，有四筆資料進資料庫了 ( 而且一筆資料還是錯的 )，

(有些資料庫你會發現只寫進 3 筆而已, 因為第 4 筆開始發生錯誤)

![alt tag](https://i.imgur.com/dz0uW2E.png)

他也違反了ACID 的原則，應該全部的資料都不能進資料庫，也就是好像什麼事情都沒發生過一樣。

現在我們必須解決這個問題，接著往下看，

有 transaction 的情況，

[models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)

```python
def create_items_with_transaction(**kwargs):
    count = int(kwargs.get('count'))
    result_code = 200
    try:
        with transaction.atomic():
            for i in range(0, count):
                if i == count - 2:
                    Item.objects.create(stock=100, price='error')
                else:
                    Item.objects.create(stock=100, price=10)
    except Exception as e:
        Exception('Unexpected error: {}'.format(e))
        result_code = 500
    return result_code
```

透過 Django 的 `transaction.atomic()` 來解決這個問題，

更多的 transaction 介紹可參考 [https://docs.djangoproject.com/en/1.11/topics/db/transactions/](https://docs.djangoproject.com/en/1.11/topics/db/transactions/)，

其實 `transaction.atomic()` 的用法就像是 [context-manager](https://docs.python.org/3/glossary.html#term-context-manager)，

context-manager 也可以參考我之前寫的簡單範例 [context_manager_tutorial.py](https://github.com/twtrubiks/python-notes/blob/master/context_manager_tutorial.py)。

我們再執行一次，

![alt tag](https://i.imgur.com/UxNRuEJ.png)

這時候你會發現，任何一筆資料都沒有進入資料庫，這就符合 ACID 的原則。

![alt tag](https://i.imgur.com/EBnb4QU.png)

從 Console 中可以發現，雖然有 insert 資料，但因為 transaction 的關係 rollback  了

![alt tag](https://i.imgur.com/8qmYtrn.png)

看完了 Atomicity 的例子，

我們再來看一個 Consistency 以及 Isolation 的例子，

* [Youtube Tutorial PART 4 - Django 實戰 Transaction - Consistency and Isolation](https://youtu.be/m7JIHU9mLW4)

在這個例子中，模擬有兩個人同時對 id =1 的這筆資料操作，其中一個人對 stock 欄位一直進貨 (+1)，

另一個人對 stock 欄位一直取貨 (-1)，分別執行 100 次，我們來觀察他的結果，

[models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)

```python
def data_no_consistency_purchase(delay=0.02):
    for i in range(0, 100):
        item = Item.objects.get(id=1)
        item.stock = item.stock + 1
        item.save()
        time.sleep(delay)
    print('data_no_consistency_purchase done')


def data_no_consistency_pick_up(delay=0.05):
    for i in range(0, 100):
        item = Item.objects.get(id=1)
        item.stock = item.stock - 1
        item.save()
        time.sleep(delay)
    print('data_no_consistency_pick_up done')


def data_no_consistency():
    threading.Thread(target=data_no_consistency_purchase).start()
    threading.Thread(target=data_no_consistency_pick_up).start()
    return 200
```

先來看一下，id = 1 的資料

![alt tag](https://i.imgur.com/EBnb4QU.png)

執行一次

![alt tag](https://i.imgur.com/iqtcg6F.png)

當你從 Console 中看到下圖，代表 thread 跑完

![alt tag](https://i.imgur.com/ez6KOFI.png)

![alt tag](https://i.imgur.com/Zn8NJ6G.png)

執行結果，

![alt tag](https://i.imgur.com/ZupFKbR.png)

你會發現很怪，為什麼呢:question:

理論上，id = 1 的 stock 應該還是要維持 100（ 原始的 stock =100 ），因為兩個使用者分別

取貨和進貨 100 次，可是你會發現結果竟然不是 100:scream:

疑:question::question::question::question:

為什麼會這樣呢 :question::question::question:

因為有可能在我們取出 stock 欄位時，更新完了之後，在要寫回去資料庫時，已經有別人比你

更快完成了（ 並且寫入資料庫 ），導致其實你拿到的 stock 欄位是舊的 ( [Dirty reads](https://en.wikipedia.org/wiki/Isolation_%28database_systems%29#Dirty_readshttps://zh.wikipedia.org/wiki/) )，所以

寫進去當然也是錯的。

這就是前面在 Isolation 中提到的多個並發交易必須防止的錯誤，

那該如何解決這類的問題呢？

有兩種方法可以解決，分別是 **Pessimistic（ 悲觀 ）** 以及 **Optimistic（ 樂觀 ）** 兩種方法，

***Pessimistic***

[models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)

```python
def consistency_pessimistic_purchase(delay=0.02):
    for i in range(0, 100):
        try:
            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=1)
                item.stock = item.stock + 1
                item.save()
                time.sleep(delay)
        except Exception as e:
            Exception('Unexpected error: {}'.format(e))
    print('data_no_consistency_pick_up done')


def consistency_pessimistic_pick_up(delay=0.05):
    for i in range(0, 100):
        try:
            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=1)
                item.stock = item.stock - 1
                item.save()
                time.sleep(delay)
        except Exception as e:
            Exception('Unexpected error: {}'.format(e))
    print('data_no_consistency_pick_up done')


def data_consistency():
    """ use pessimistic """
    threading.Thread(target=consistency_pessimistic_purchase).start()
    threading.Thread(target=consistency_pessimistic_pick_up).start()
    return 200
```

透過 Django 中的 `transaction.atomic()` 以及 `select_for_update()` 來完成，

`select_for_update()` 可參考 Django 官網的 [select-for-update](https://docs.djangoproject.com/en/2.0/ref/models/querysets/#select-for-update) 說明，以下為官網部分說明

```text
Returns a queryset that will lock rows until the end of the transaction, generating a SELECT ... FOR UPDATE SQL statement on supported databases.
```

主要就是透過 SQL 中的 `SELECT ... FOR UPDATE` 語法將目前的 row 鎖定，必須等他交易結束，

其他的人才可以使用這個 row，這邊也要注意，要看 databases 有沒有支援這個語法，

像是 [MySQL](https://www.mysql.com/cn/) 以及 [PostgreSQL](https://www.postgresql.org/) 就有支援，[SQLite](https://www.sqlite.org/index.html) 則沒有支援。

透過這個方法，

![alt tag](https://i.imgur.com/ZidsEvg.png)

執行後你會發現，不管我們執行 100 次或 1000 次，id = 1 的 stock 都是維持 100。

![alt tag](https://i.imgur.com/yxiMWWg.png)

***Optimistic***

[models.py](https://github.com/twtrubiks/django-transactions-tutorial/blob/master/items/models.py)

```python
def consistency_optimistic_purchase(delay=0.01):
    i = 0
    """use version (add field) track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        version = old_item.version
        item = Item.objects.filter(id=1, version=version).update(stock=stock + 1, version=version + 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_purchase)')
        time.sleep(delay)
    """use stock track of changes """
    # while i < 100:
    #     old_item = Item.objects.get(id=1)
    #     stock = old_item.stock
    #     item = Item.objects.filter(id=1, stock=stock).update(stock=stock + 1)
    #     if item:
    #         i += 1
    #     else:
    #         print('item is null (optimistic_purchase)')
    #     time.sleep(delay)
    print('data_no_consistency_purchase done')
    return 200


def consistency_optimistic_pick_up(delay=0.02):
    i = 0
    """use version (add field) track of changes """
    while i < 100:
        old_item = Item.objects.get(id=1)
        stock = old_item.stock
        version = old_item.version
        item = Item.objects.filter(id=1, version=version).update(stock=stock - 1, version=version + 1)
        if item:
            i += 1
        else:
            print('item is null (optimistic_pick_up)')
        time.sleep(delay)
    """use stock track of changes """
    # while i < 100:
    #     old_item = Item.objects.get(id=1)
    #     stock = old_item.stock
    #     item = Item.objects.filter(id=1, stock=stock).update(stock=stock - 1)
    #     if item:
    #         i += 1
    #     else:
    #         print('item is null (optimistic_pick_up)')
    #     time.sleep(delay)
    print('data_no_consistency_purchase done')
    return 200

def data_consistency():
    """ use optimistic """
    threading.Thread(target=consistency_optimistic_purchase).start()
    threading.Thread(target=consistency_optimistic_pick_up).start()
    return 200
```

這邊提供兩種方法給大家，其中一種是增加一個欄位去追蹤目前的變化 ( version 這個欄位 )，

每次都會將 version 帶入查詢條件，並且如果成功更新，就加一 ; 另一種方法是不增加一個欄位，直接將 stock

帶入條件查詢（ 也就是註解的部份 ）。

這邊你可能會問我為什麼需要下列這段 code

```python
item = Item.objects.filter(id=1, version=version).update(stock=stock - 1, version=version + 1)
if item:
    i += 1
else:
    print('item is null (optimistic_pick_up)')
```

首先，會將 version 帶入條件查詢，主要就是避免取到舊的資料 ( 可能別人提前你一步更新資料了 )，所以說，

有可能，item 取出來是空的，為什麼呢？因為別人提前你一步更新資料了，version 已經變掉了（ 被加1 ），

這段 code 也用來保證取貨和進貨都會成功更新資料 100 次。（ 這其實不難，多想一下你就會了解了 :grinning:）

### Pessimistic vs Optimistic

如果你的系統同時間會有很高的機率同時修改一筆資料，

適合使用 Pessimistic (悲觀) 的方法。

如果你的系統同時間修改一筆資料的機率非常低或是使用者較少以及大部分都是讀取的操作，

適合使用 Optimistic (樂觀) 的方法。

## 後記

這次帶大家了解 transactions 的一些基本概念，也透過一些簡單的範例加深以及幫助大家理解他 ( transactions )，

其實我也只介紹了一小部分，這部份還有很多可以研究，相信如果有認真看的你一定會覺得該去看資料庫了，

沒錯，很多都是資料庫的概念，所以如果還有興趣，大家可以用一些文章內提到的關鍵字去 google ，這次就

介紹到這邊了，謝謝大家～

## 執行環境

* Python 3.6.2

## Reference

* [Django](https://www.djangoproject.com/)
* [Django-REST-framework](http://www.django-rest-framework.org/)
* [PyMySQL](https://github.com/PyMySQL/PyMySQL)
* [Transaction Isolation - wiki](https://zh.wikipedia.org/wiki/%E4%BA%8B%E5%8B%99%E9%9A%94%E9%9B%A2)
* [How to manage concurrency in Django models](https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2)
* [PESSIMISTIC vs. OPTIMISTIC concurrency control](https://www.ibm.com/support/knowledgecenter/en/SSPK3V_7.0.0/com.ibm.swg.im.soliddb.sql.doc/doc/pessimistic.vs.optimistic.concurrency.control.html)

## Donation

文章都是我自己研究內化後原創，如果有幫助到您，也想鼓勵我的話，歡迎請我喝一杯咖啡:laughing:

![alt tag](https://i.imgur.com/LRct9xa.png)

[贊助者付款](https://payment.opay.tw/Broadcaster/Donate/9E47FDEF85ABE383A0F5FC6A218606F8)

## License

MIT license
