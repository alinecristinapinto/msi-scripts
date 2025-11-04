-- Scripts para criar as tabelas do Stack Exchange Data Dump
-- Baseado na documentação oficial.
-- Nota: Chaves estrangeiras não estão incluídas para simplicidade e para evitar problemas de ordem de criação.

-- Tabela: Posts
-- Contém todas as perguntas, respostas, wikis de tags, etc.
CREATE TABLE Posts (
    Id INTEGER PRIMARY KEY,
    PostTypeId INTEGER NOT NULL,
    AcceptedAnswerId INTEGER,
    ParentId INTEGER,
    CreationDate TIMESTAMP NOT NULL,
    DeletionDate TIMESTAMP,
    Score INTEGER NOT NULL,
    ViewCount INTEGER,
    Body TEXT,
    OwnerUserId INTEGER,
    OwnerDisplayName TEXT,
    LastEditorUserId INTEGER,
    LastEditorDisplayName TEXT,
    LastEditDate TIMESTAMP,
    LastActivityDate TIMESTAMP NOT NULL,
    Title TEXT,
    Tags TEXT,
    AnswerCount INTEGER,
    CommentCount INTEGER,
    FavoriteCount INTEGER,
    ClosedDate TIMESTAMP,
    CommunityOwnedDate TIMESTAMP,
    ContentLicense TEXT
);

-- Tabela: Users
-- Contém informações sobre os usuários registrados.
CREATE TABLE Users (
    Id INTEGER PRIMARY KEY,
    Reputation INTEGER NOT NULL,
    CreationDate TIMESTAMP NOT NULL,
    DisplayName VARCHAR(40) NOT NULL,
    LastAccessDate TIMESTAMP NOT NULL,
    WebsiteUrl VARCHAR(255),
    Location VARCHAR(255),
    AboutMe TEXT,
    Views INTEGER NOT NULL,
    UpVotes INTEGER NOT NULL,
    DownVotes INTEGER NOT NULL,
    ProfileImageUrl VARCHAR(255),
    EmailHash VARCHAR(50),
    AccountId INTEGER
);

-- Tabela: Comments
-- Contém os comentários feitos nos posts.
CREATE TABLE Comments (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER NOT NULL,
    Score INTEGER NOT NULL,
    Text TEXT NOT NULL,
    CreationDate TIMESTAMP NOT NULL,
    UserDisplayName VARCHAR(40),
    UserId INTEGER,
    ContentLicense TEXT
);

-- Tabela: Badges
-- Contém as medalhas (badges) concedidas aos usuários.
CREATE TABLE Badges (
    Id INTEGER PRIMARY KEY,
    UserId INTEGER NOT NULL,
    Name VARCHAR(50) NOT NULL,
    Date TIMESTAMP NOT NULL,
    Class SMALLINT NOT NULL,
    TagBased BOOLEAN NOT NULL
);

-- Tabela: PostHistory
-- Contém o histórico de revisões de cada post.
CREATE TABLE PostHistory (
    Id INTEGER PRIMARY KEY,
    PostHistoryTypeId INTEGER NOT NULL,
    PostId INTEGER NOT NULL,
    RevisionGUID UUID NOT NULL,
    CreationDate TIMESTAMP NOT NULL,
    UserId INTEGER,
    UserDisplayName VARCHAR(40),
    Comment TEXT,
    Text TEXT,
    ContentLicense TEXT
);

-- Tabela: PostLinks
-- Armazena links entre posts, como posts duplicados ou relacionados.
CREATE TABLE PostLinks (
    Id INTEGER PRIMARY KEY,
    CreationDate TIMESTAMP NOT NULL,
    PostId INTEGER NOT NULL,
    RelatedPostId INTEGER NOT NULL,
    LinkTypeId INTEGER NOT NULL
);

-- Tabela: PostTags
-- Tabela de junção que mapeia posts às suas tags.
CREATE TABLE PostTags (
    PostId INTEGER NOT NULL,
    TagId INTEGER NOT NULL,
    PRIMARY KEY (PostId, TagId)
);

-- Tabela: Tags
-- Contém todas as tags usadas no site.
CREATE TABLE Tags (
    Id INTEGER PRIMARY KEY,
    TagName VARCHAR(150) NOT NULL,
    Count INTEGER NOT NULL,
    ExcerptPostId INTEGER,
    WikiPostId INTEGER,
    IsModeratorOnly BOOLEAN,
    IsRequired BOOLEAN
);

-- Tabela: Votes
-- Armazena os votos dados em posts, como upvotes, downvotes e favoritos.
CREATE TABLE Votes (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER NOT NULL,
    VoteTypeId INTEGER NOT NULL,
    UserId INTEGER,
    CreationDate DATE,
    BountyAmount INTEGER
);

-- Tabela: SuggestedEdits
-- Contém as edições sugeridas por usuários com baixa reputação.
CREATE TABLE SuggestedEdits (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER NOT NULL,
    CreationDate TIMESTAMP NOT NULL,
    ApprovalDate TIMESTAMP,
    RejectionDate TIMESTAMP,
    OwnerUserId INTEGER,
    Comment TEXT,
    Text TEXT,
    Title TEXT,
    Tags TEXT,
    RevisionGUID UUID
);
