const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TrendRegistry", function () {
  let registry;
  let owner;
  let creator;
  let analyst;

  const trend = {
    title: "AI replacing interns in startups",
    category: "Founder Culture",
    score: 91,
    contentHash: "0x5f8b9f3a2e4d7c6b1a0f9e8d7c6b5a4938271615141312111009080706050403",
  };

  beforeEach(async function () {
    [owner, creator, analyst] = await ethers.getSigners();

    const Registry = await ethers.getContractFactory("TrendRegistry");
    registry = await Registry.deploy();
    await registry.waitForDeployment();
  });

  async function registerSampleTrend() {
    return registry.connect(creator).registerTrend(
      trend.title,
      trend.category,
      trend.score,
      trend.contentHash
    );
  }

  it("registers a trend with a numeric id, timestamp, content hash, and creator", async function () {
    await expect(registerSampleTrend())
      .to.emit(registry, "TrendRegistered")
      .withArgs(1, trend.title, creator.address);

    const stored = await registry.getTrend(1);
    expect(stored.id).to.equal(1);
    expect(stored.title).to.equal(trend.title);
    expect(stored.category).to.equal(trend.category);
    expect(stored.score).to.equal(trend.score);
    expect(stored.contentHash).to.equal(trend.contentHash);
    expect(stored.creator).to.equal(creator.address);
    expect(stored.verified).to.equal(false);
    expect(stored.firstSeen).to.be.greaterThan(0);
    expect(await registry.trendCount()).to.equal(1);
    expect(await registry.creatorReputation(creator.address)).to.equal(1);
  });

  it("registers multiple trends with incrementing ids", async function () {
    await registerSampleTrend();
    await registry.connect(analyst).registerTrend(
      "Kenyan SMEs selling through WhatsApp",
      "Business",
      84,
      "0x7f8b9f3a2e4d7c6b1a0f9e8d7c6b5a4938271615141312111009080706050403"
    );

    expect(await registry.trendCount()).to.equal(2);
    expect((await registry.getTrend(2)).creator).to.equal(analyst.address);
  });

  it("rejects empty metadata", async function () {
    await expect(
      registry.registerTrend("", trend.category, trend.score, trend.contentHash)
    ).to.be.revertedWithCustomError(registry, "EmptyTitle");

    await expect(
      registry.registerTrend(trend.title, "", trend.score, trend.contentHash)
    ).to.be.revertedWithCustomError(registry, "EmptyCategory");

    await expect(
      registry.registerTrend(trend.title, trend.category, trend.score, "")
    ).to.be.revertedWithCustomError(registry, "EmptyContentHash");
  });

  it("updates score snapshots as velocity changes", async function () {
    await registerSampleTrend();

    await expect(registry.connect(analyst).updateScore(1, 97))
      .to.emit(registry, "TrendScoreUpdated")
      .withArgs(1, trend.score, 97);

    expect((await registry.getTrend(1)).score).to.equal(97);
  });

  it("updates the AI content hash", async function () {
    await registerSampleTrend();

    const updatedHash = "0x9f8b9f3a2e4d7c6b1a0f9e8d7c6b5a4938271615141312111009080706050403";
    await expect(registry.connect(analyst).updateContentHash(1, updatedHash))
      .to.emit(registry, "ContentHashUpdated")
      .withArgs(1, updatedHash);

    expect((await registry.getTrend(1)).contentHash).to.equal(updatedHash);
    expect(await registry.creatorReputation(analyst.address)).to.equal(1);
  });

  it("lets only the owner verify trends", async function () {
    await registerSampleTrend();

    await expect(registry.connect(analyst).verifyTrend(1))
      .to.be.revertedWithCustomError(registry, "NotOwner");

    await expect(registry.verifyTrend(1))
      .to.emit(registry, "TrendVerified")
      .withArgs(1);

    expect((await registry.getTrend(1)).verified).to.equal(true);
    expect(await registry.creatorReputation(creator.address)).to.equal(4);
  });

  it("reverts when reading or updating a missing trend", async function () {
    await expect(registry.getTrend(1))
      .to.be.revertedWithCustomError(registry, "TrendNotFound")
      .withArgs(1);

    await expect(registry.updateScore(1, 90))
      .to.be.revertedWithCustomError(registry, "TrendNotFound")
      .withArgs(1);
  });
});
