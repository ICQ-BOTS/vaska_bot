import tarantool

connection = tarantool.connect("89.208.198.172", 3305)

space_phrases = connection.space('phrases')

space_answer = connection.space('question')

space_user = connection.space('user')

space_sticker = connection.space('sticker')


class User:
	def __init__(self, user_id,):
		self.user = space_user.select(user_id)
		self.user_id = user_id

	def get(self):
		if not self.user:
			self.user = space_user.insert((self.user_id, False, {'text': None}))
		
		self.space = self.user[0]
		self.example = self.space[1]
		self.old_mes = self.space[2]
		return self

	def save(self):
		space_user.replace(self.user[0])       
		