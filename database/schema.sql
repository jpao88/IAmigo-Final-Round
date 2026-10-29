-- IAmigo V1 · Esquema de la base de datos (MySQL 8)
-- Generado desde docs/modelo-de-datos.md. Si cambia el modelo, actualizar ambos.
-- Se puede ejecutar más de una vez: no borra nada y solo crea lo que falta.

CREATE DATABASE IF NOT EXISTS iamigo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE iamigo;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  senha_hash VARCHAR(255) NOT NULL,
  papel ENUM('usuario', 'admin') NOT NULL DEFAULT 'usuario',
  limite_hoje TINYINT UNSIGNED NOT NULL DEFAULT 3,
  onboarding_concluido BOOLEAN NOT NULL DEFAULT FALSE,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_limite_hoje CHECK (limite_hoje BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS tarefas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  data_planejada DATE NULL,
  ordem_dia TINYINT UNSIGNED NULL,
  concluida BOOLEAN NOT NULL DEFAULT FALSE,
  concluida_em DATETIME NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_tarefas_usuario_data (usuario_id, data_planejada)
);

CREATE TABLE IF NOT EXISTS passos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tarefa_id INT NOT NULL,
  texto VARCHAR(255) NOT NULL,
  ordem SMALLINT UNSIGNED NOT NULL,
  minutos_estimados SMALLINT UNSIGNED NOT NULL DEFAULT 10,
  gerado_por_ia BOOLEAN NOT NULL DEFAULT FALSE,
  concluido BOOLEAN NOT NULL DEFAULT FALSE,
  concluido_em DATETIME NULL,
  substituido BOOLEAN NOT NULL DEFAULT FALSE,
  passo_origem_id INT NULL,
  FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
  FOREIGN KEY (passo_origem_id) REFERENCES passos(id) ON DELETE SET NULL,
  INDEX idx_passos_tarefa_ordem (tarefa_id, ordem)
);

CREATE TABLE IF NOT EXISTS fechamentos_dia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  data DATE NOT NULL,
  fechado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  UNIQUE KEY uq_fechamento_usuario_data (usuario_id, data)
);
