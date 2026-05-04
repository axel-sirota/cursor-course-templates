package users

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// UserRepository defines the persistence operations for users.
// Defined here at the consumer (service) side.
type UserRepository interface {
	Create(ctx context.Context, user User) (User, error)
	GetByID(ctx context.Context, id int64) (User, error)
	List(ctx context.Context) ([]User, error)
}

type postgresUserRepository struct {
	pool *pgxpool.Pool
}

// NewPostgresUserRepository creates a new postgres-backed UserRepository.
func NewPostgresUserRepository(pool *pgxpool.Pool) UserRepository {
	return &postgresUserRepository{pool: pool}
}

func (r *postgresUserRepository) Create(ctx context.Context, user User) (User, error) {
	const q = `
		INSERT INTO users (name, email, created_at)
		VALUES ($1, $2, $3)
		RETURNING id, name, email, created_at`

	user.CreatedAt = time.Now()
	err := r.pool.QueryRow(ctx, q, user.Name, user.Email, user.CreatedAt).
		Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)
	if err != nil {
		return User{}, fmt.Errorf("inserting user: %w", err)
	}
	return user, nil
}

func (r *postgresUserRepository) GetByID(ctx context.Context, id int64) (User, error) {
	const q = `SELECT id, name, email, created_at FROM users WHERE id = $1`

	var user User
	err := r.pool.QueryRow(ctx, q, id).
		Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)
	if err != nil {
		return User{}, fmt.Errorf("querying user %d: %w", id, err)
	}
	return user, nil
}

func (r *postgresUserRepository) List(ctx context.Context) ([]User, error) {
	const q = `SELECT id, name, email, created_at FROM users ORDER BY id`

	rows, err := r.pool.Query(ctx, q)
	if err != nil {
		return nil, fmt.Errorf("listing users: %w", err)
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		if err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt); err != nil {
			return nil, fmt.Errorf("scanning user row: %w", err)
		}
		users = append(users, u)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterating user rows: %w", err)
	}
	return users, nil
}
