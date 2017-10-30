from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
Base = declarative_base()


class AuctionSystem(object):

    def __init__(self):
        self.engine = create_engine('sqlite:///auction.db')
        try:
            Base.metadata.create_all(self.engine)
        except:
            pass
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)

    def register_user(self, id, name, password):
        session = self.DBSession()
        user = User(id=id, name=name, password=password)
        self.add_row(session, user)

    def post_item(self, owner_id, item_id, name, desc):
        seller = self.query_user(owner_id)
        session = self.DBSession()
        item = Item(id=item_id, name=name, desc=desc, seller_id=owner_id, seller=seller)
        self.add_row(session, item)

    def make_bid(self, bid_id, user_id, item_id, price):
        user = self.query_user(user_id)
        item = self.query_item(item_id)
        session = self.DBSession()
        bid = Bid(id=bid_id, bidder_id=user_id, item_id=item_id, bidder=user, item=item,price=price)
        self.add_row(session, bid)

    def query_item(self, item_id):
        session = self.DBSession()
        item = session.query(Item).filter(Item.id == item_id).one()
        session.close()
        return item

    def query_user(self, user_id):
        session = self.DBSession()
        user = session.query(User).filter(User.id == user_id).one()
        session.close()
        if user is not None:
            return user
        else: return None

    def add_row(self, session, row):
        session.add(row)
        session.commit()
        session.close()

    def get_items(self, item_id):
        item = self.query_item(item_id)
        seller = self.query_user(item.seller_id)
        if item is not None:
            print("Item name: " + item.name + ", Description: " + item.desc + ", Seller: " + seller.name + "\n")
        else:
            return None

    def get_user(self, user_id):
        user = self.query_user(user_id)
        if user is None:
            print("User not found!")
        else:
            print("User name: " + user.name + ", Password: " + user.password + "\n")

    def search_posts(self, user_id):
        user = self.query_user(user_id)
        session = self.DBSession()
        items = session.query(Item).filter(Item.seller == user)
        session.close()
        print(user.name + "'s Post: ")
        for item in items:
            print("Item: " + item.name + ", Description: " + item.desc)
        print()

    def search_user_bids(self, user_id):
        user = self.query_user(user_id)
        session = self.DBSession()
        bids = session.query(Bid).filter(Bid.bidder == user)
        print(user.name + "'s Bids: ")
        for bid in bids:
            print("item: " + bid.item.name + ", bidder: " + bid.bidder.name + ", price " +str(bid.price))
        print()

    def search_item_bids(self, item_id):
        item = self.query_item(item_id)
        session = self.DBSession()
        bids = session.query(Bid).filter(Bid.item == item)
        print(item.name + "'s Bids: ")
        for bid in bids:
            print("item: " + bid.item.name + ", bidder: " + bid.bidder.name + ", price " + str(bid.price))
        print()


class User(Base):

    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)


class Item(Base):

    __tablename__ = 'ITEM'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    seller_id = Column(Integer, ForeignKey(User.id))
    seller = relationship(User)


class Bid(Base):

    __tablename__ = 'BID'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey(User.id))
    bidder_id = Column(Integer, ForeignKey(Item.id))
    price = Column(Integer)
    bidder = relationship(User)
    item = relationship(Item)


