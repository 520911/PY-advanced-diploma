import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from vk_class.class_user import VkUser

db = 'postgresql://postgres:520911@localhost/vk'
engine = sq.create_engine(db)

Base = declarative_base()
Session = sessionmaker(bind=engine)
Session.configure()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    ids = sq.Column(sq.Integer, nullable=False)
    name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    relation = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)


class Matches(Base):
    __tablename__ = 'matches'

    id = sq.Column(sq.Integer, primary_key=True)
    ids = sq.Column(sq.Integer, nullable=False)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    domain = sq.Column(sq.String)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))
    user = relationship(User)


class Photos(Base):
    __tablename__ = 'photos'

    id = sq.Column(sq.Integer, primary_key=True)
    raiting = sq.Column(sq.Integer)
    link = sq.Column(sq.String)
    matches_id = sq.Column(sq.Integer, sq.ForeignKey('matches.id'))
    match = relationship(Matches)


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = sq.Column(sq.Integer, primary_key=True)
    match_id = sq.Column(sq.Integer, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))
    user = relationship(User)


def add_user_to_db(info: VkUser):
    session = Session()
    user_info = info.get_user_info()
    db_user = User(ids=user_info['id'], name=user_info['first_name'], last_name=user_info['last_name'],
                   relation=user_info['relation'],
                   sex=user_info['sex'])
    session.add(db_user)
    session.commit()
    return db_user


def add_to_black_list(user_id, match_id):
    session = Session()
    black_user = BlackList(match_id=match_id, user_id=user_id)
    session.add(black_user)
    session.commit()


def save_matches(info: VkUser, count=None):
    session = Session()
    user = add_user_to_db(info)
    db_match = info.get_search_info()
    item_match = Matches(ids=db_match[count]['id'], first_name=db_match[count]['first_name'],
                         last_name=db_match[count]['last_name'], domain=db_match[count]['domain'], user=user)
    item_photo = []
    for photo in info.get_top_photos(db_match[count]['id']):
        item_photo.append(Photos(raiting=photo[1],
                                 link=photo[0],
                                 match=item_match))
        session.add(item_match)
        session.add_all(item_photo)
    session.commit()


# Base.metadata.create_all(engine)
# Base.metadata.drop_all(engine)
