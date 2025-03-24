from app.common.models.SimpleMessage import (
    SimpleMessage
)
from app.message.Message import (
    MessageBase,
    MessageCreate,
    MessageUpdate,
    Message,
    MessagePublic,
    MessagesPublic,
)
from app.user.User import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    User,
    UserPublic,
)
from app.chat.Chat import (
    ChatBase,
    ChatCreate,
    Chat
)
from app.avatar.Avatar import (
    AvatarBase,
    AvatarCreate,
    AvatarUpdate,
    Avatar
)
from app.train_data.TrainData import (
    TrainDataBase,
    TrainDataCreate,
    TrainData
)

SimpleMessage.model_rebuild()
Message.model_rebuild()
User.model_rebuild()
Chat.model_rebuild()
Avatar.model_rebuild()
