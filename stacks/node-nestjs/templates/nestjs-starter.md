# NestJS Starter — Feature Module Structure

## Directory Layout

```
src/
  main.ts                          # Bootstrap: global pipes, interceptors, swagger
  app.module.ts                    # Root module: imports features + infrastructure
  users/
    users.module.ts
    users.controller.ts
    users.controller.spec.ts
    users.service.ts
    users.service.spec.ts
    users.repository.ts            # TypeORM wrapper or Prisma service
    dto/
      create-user.dto.ts
      update-user.dto.ts
      user-response.dto.ts
    entities/
      user.entity.ts
    guards/
      (resource-specific guards, if needed)
  shared/
    guards/
      jwt-auth.guard.ts
    interceptors/
      logging.interceptor.ts
    filters/
      http-exception.filter.ts
    pipes/
      (global pipes registered in main.ts, not here)
test/
  users.e2e-spec.ts
  jest-e2e.json
```

---

## `main.ts`

```typescript
import { NestFactory, Reflector } from '@nestjs/core';
import { ValidationPipe, ClassSerializerInterceptor } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global validation — strip unknown fields, reject invalid input
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,               // strip properties without decorators
      forbidNonWhitelisted: true,    // throw 400 for unknown properties
      transform: true,               // auto-transform payload to DTO class instances
    }),
  );

  // Global serializer — respects @Exclude() on entities/DTOs
  app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));

  // Swagger — auto-generated API docs at /api
  const config = new DocumentBuilder()
    .setTitle('API')
    .setDescription('API documentation')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  await app.listen(process.env.PORT ?? 3000);
}

bootstrap();
```

---

## `app.module.ts`

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersModule } from './users/users.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        url: config.get<string>('DATABASE_URL'),
        autoLoadEntities: true,
        synchronize: config.get('NODE_ENV') === 'development', // never true in production
      }),
    }),
    UsersModule,
    // add feature modules here
  ],
})
export class AppModule {}
```

---

## `users/users.module.ts`

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { UsersRepository } from './users.repository';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],         // export service for other modules to inject
})
export class UsersModule {}
```

---

## `users/users.controller.ts` (skeleton)

```typescript
import { Controller, Get, Post, Body, Param, ParseUUIDPipe, UseGuards } from '@nestjs/common';
import { ApiTags, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../shared/guards/jwt-auth.guard';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';

@ApiTags('users')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Get()
  findAll() {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.usersService.findOne(id);
  }
}
```

---

## `shared/guards/jwt-auth.guard.ts`

```typescript
import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
```

---

## Phase 0 Bootstrap Commands

```bash
# 1. Create new NestJS project
npx @nestjs/cli new my-api --package-manager npm

# 2. Install required dependencies
npm install typeorm @nestjs/typeorm pg class-validator class-transformer \
  @nestjs/passport passport-jwt @nestjs/swagger @nestjs/config

npm install -D @types/passport-jwt supertest @types/supertest

# 3. Generate feature modules
nest g module users
nest g controller users
nest g service users

# 4. Verify TypeScript compiles
npx tsc --noEmit

# 5. Run tests
npm test
```
