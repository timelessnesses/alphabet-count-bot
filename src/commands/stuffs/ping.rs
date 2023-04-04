use crate::{Context, Error};
use chrono;
use poise;
use poise::serenity_prelude as poise_serenity;

#[poise::command(prefix_command, slash_command)]
pub async fn ping(ctx: Context<'_>) -> Result<(), Error> {
    ctx.defer().await.unwrap();
    let shard = ctx.framework().shard_manager.lock().await;
    let shard = shard.runners.lock().await;
    let ping = shard.get(&poise_serenity::ShardId(ctx.serenity_context().shard_id));
    let j = ping.unwrap().latency;
    if j.is_none() || ping.is_none() {
        ctx.send(
            |h| {
                h.embed(|e| {
                    return e.title("Failed to fetch shard!").description("Something is wrong at the bot's end. Please consider send this error to GitHub repository issue!").color(poise_serenity::Color::RED).timestamp(chrono::prelude::Local::now())
                });
                return h;
            }
        ).await.unwrap();
        return Err(("Failed to fetch shard!").into());
    }
    ctx.send(|h| {
        h.embed(|e| {
            return e
                .title("Pong!")
                .description(format!(
                    "Shard latency: {}ms\nShard ID: {}",
                    j.unwrap().as_millis(),
                    ctx.serenity_context().shard_id
                ))
                .color(poise_serenity::Color::DARK_GREEN)
                .timestamp(chrono::prelude::Local::now());
        })
    })
    .await
    .unwrap();
    return Ok(());
}