CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15)
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    available INT NOT NULL
);

CREATE TABLE borrowing (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id),
    equipment_id INT REFERENCES equipment(id),
    quantity INT NOT NULL,
    issue_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'Borrowed'
);

INSERT INTO equipment (name, quantity, available)
VALUES
('Cricket Bat', 15, 15),
('Helmet', 20, 20),
('Pads', 12, 12),
('Practice Balls', 30, 30),
('Gloves', 15, 15);